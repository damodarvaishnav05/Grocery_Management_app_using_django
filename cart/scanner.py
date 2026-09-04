import re
from decimal import Decimal
from django.db.models import Q
from products.models import Product


def parse_line_quantity_and_query(raw_line):
    """
    Extracts numerical quantity, unit, and clean search keywords from a single line.
    Example: '2 litres cow milk' -> quantity=2, unit='litres', query='cow milk'
             '1 packet whole wheat bread' -> quantity=1, unit='packet', query='whole wheat bread'
             '12 eggs' -> quantity=1, query='eggs' (or quantity=12 if unit eggs)
             'surf excel' -> quantity=1, query='surf excel'
    """
    line = raw_line.strip()
    # Remove leading symbols like '-', '*', '•'
    line = re.sub(r'^\s*[-*•]+\s*', '', line).strip()
    # Remove numbered list prefixes like '1.', '1)', '1 -'
    line = re.sub(r'^\s*\d+[\.\)\-]\s*', '', line).strip()

    # Pattern for number + optional unit (ordered longest to shortest to prevent prefix stealing)
    pattern = r'^\s*(\d+(?:\.\d+)?)\s*(kilograms?|kilos?|kg|grams?|gm|g|litres?|liters?|ltr|l|ml|packets?|packs?|pkts?|bottles?|boxes?|box|dozens?|cans?|can|bars?|pcs?|pieces?)?\s*(?:of\s+)?(.*)$'
    match = re.match(pattern, line, re.IGNORECASE)

    if match:
        raw_qty, unit, rest = match.groups()
        try:
            qty = int(float(raw_qty))
            qty = max(1, qty)
        except (ValueError, TypeError):
            qty = 1
        unit = unit.lower() if unit else ""
        query = rest.strip() if rest and rest.strip() else line
    else:
        qty = 1
        unit = ""
        query = line

    # Strip extraneous punctuation
    query = re.sub(r'[^\w\s-]', ' ', query).strip()
    query = re.sub(r'\s+', ' ', query)

    return qty, unit, query


def find_best_product_match(query, products_cache=None):
    """
    Finds the highest-confidence matching Product from the in-stock catalog.
    Uses token overlap, substring matching, and category contextual weighting.
    """
    if not query:
        return None, 0

    if products_cache is None:
        products_cache = list(Product.objects.filter(available=True).select_related("category"))

    query_lower = query.lower()
    query_tokens = set(re.findall(r'\w+', query_lower))

    # Stop words to deprioritize in comparison
    stop_words = {"fresh", "organic", "pure", "best", "good", "packet", "bottle", "box", "kg", "litre", "liter", "and", "of"}
    informative_tokens = query_tokens - stop_words
    if not informative_tokens:
        informative_tokens = query_tokens

    best_product = None
    best_score = 0

    for prod in products_cache:
        prod_name_lower = prod.name.lower()
        prod_tokens = set(re.findall(r'\w+', prod_name_lower))
        cat_name_lower = prod.category.name.lower() if prod.category else ""

        score = 0

        # Exact match
        if query_lower == prod_name_lower:
            score = 100
        # Substring in name
        elif query_lower in prod_name_lower:
            score = 90
        elif prod_name_lower in query_lower:
            score = 85
        else:
            # Token overlap
            matching_tokens = informative_tokens.intersection(prod_tokens)
            if matching_tokens:
                overlap_ratio = len(matching_tokens) / len(informative_tokens)
                score = int(overlap_ratio * 75)

                # Bonus if all informative tokens matched
                if len(matching_tokens) == len(informative_tokens):
                    score += 15

                # Bonus for category match
                if any(t in cat_name_lower for t in informative_tokens):
                    score += 5

        # Brand / Specific token bonuses (e.g. Ariel, Surf, Coke, Milk, Bread, Potato)
        for key in ["ariel", "surf", "milk", "egg", "bread", "paneer", "potato", "onion", "tomato", "mango", "apple", "banana", "coke", "sprite", "fanta", "rice", "oil", "atta"]:
            if key in query_lower and key in prod_name_lower:
                score += 10
                break

        if score > best_score:
            best_score = score
            best_product = prod

    if best_score >= 35:
        return best_product, min(best_score, 100)
    return None, 0


def parse_and_match_grocery_list(raw_text):
    """
    Parses full grocery list text, splits into individual items,
    and matches against catalog with stock and subtotal calculations.
    """
    if not raw_text or not raw_text.strip():
        return {
            "matches": [],
            "unmatched": [],
            "total_items": 0,
            "matched_count": 0,
            "estimated_total": Decimal("0.00"),
        }

    # Split by newlines, commas, or semicolons
    raw_lines = [l.strip() for l in re.split(r'[\r\n;]+', raw_text) if l.strip()]

    # Fetch catalog once for fast memory matching
    products_cache = list(Product.objects.filter(available=True).select_related("category"))

    matches = []
    unmatched = []
    seen_product_ids = set()

    for line in raw_lines:
        qty, unit, query = parse_line_quantity_and_query(line)
        if not query:
            continue

        product, confidence = find_best_product_match(query, products_cache)

        if product:
            # Avoid duplicate rows by incrementing quantity if same product detected
            if product.id in seen_product_ids:
                for m in matches:
                    if m["product"].id == product.id:
                        m["requested_quantity"] += qty
                        m["allocated_quantity"] = min(m["requested_quantity"], product.stock)
                        m["subtotal"] = product.final_price * m["allocated_quantity"]
                        break
                continue

            seen_product_ids.add(product.id)
            in_stock = product.stock > 0
            allocated_qty = min(qty, product.stock) if in_stock else 0
            subtotal = product.final_price * allocated_qty

            matches.append({
                "original_line": line,
                "query": query,
                "unit": unit,
                "requested_quantity": qty,
                "allocated_quantity": allocated_qty,
                "product": product,
                "confidence": confidence,
                "in_stock": in_stock,
                "subtotal": subtotal,
                "selected": in_stock,
            })
        else:
            unmatched.append({
                "original_line": line,
                "query": query,
                "requested_quantity": qty,
            })

    estimated_total = sum(m["subtotal"] for m in matches if m["selected"])

    return {
        "matches": matches,
        "unmatched": unmatched,
        "total_items": len(raw_lines),
        "matched_count": len(matches),
        "estimated_total": estimated_total,
    }
