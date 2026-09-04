import json
import re
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.db.models import Avg
from django.core.paginator import Paginator
from django.http import JsonResponse

from .models import Product
from reviews.models import Review
from reviews.forms import ReviewForm
from categories.models import Category
from cart.models import Cart
from cart.scanner import find_best_product_match, parse_line_quantity_and_query



def index(request):

    # Get available products
    products = Product.objects.filter(
        available=True
    ).order_by("-id")


    # Get all categories
    categories = Category.objects.all()


    # Search
    query = request.GET.get("q")

    if query:

        products = products.filter(
            name__icontains=query
        )


    # Category filter
    category_slug = request.GET.get("category")

    if category_slug:

        products = products.filter(
            category__slug=category_slug
        )



    paginator = Paginator(
        products,
        12
    )

    page_number = request.GET.get("page")

    products = paginator.get_page(
        page_number
    )



    context = {

        "products": products,

        "categories": categories,

        "query": query,

    }


    return render(
        request,
        "products/index.html",
        context
    )




def detail(request, slug):

    # Get product
    product = get_object_or_404(
        Product,
        slug=slug,
        available=True
    )


    # Get reviews
    reviews = product.reviews.all()


    # Calculate average rating
    average_rating = reviews.aggregate(
        Avg("rating")
    )["rating__avg"]


    # Get related products
    related_products = Product.objects.filter(
        category=product.category,
        available=True
    ).exclude(
        id=product.id
    )[:4]


    # Review form
    form = ReviewForm()


    # Context
    context = {

        "product": product,

        "reviews": reviews,

        "average_rating": average_rating,

        "related_products": related_products,

        "form": form,

    }


    return render(
        request,
        "products/detail.html",
        context
    )


def voice_command_api(request):
    """
    FreshVoice™ Conversational Assistant Endpoint:
    Handles voice search, direct add-to-cart, and app navigation.
    """
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            command = body.get("command", "").strip()
        except Exception:
            command = request.POST.get("command", "").strip()
    else:
        command = request.GET.get("command", "").strip()

    if not command:
        return JsonResponse({"status": "error", "message": "No voice command received."}, status=400)

    cmd_lower = command.lower().strip()

    # 1. Navigation Intents
    if any(p in cmd_lower for p in ["open cart", "go to cart", "view cart", "show cart", "my cart"]):
        return JsonResponse({
            "status": "success",
            "action": "navigate",
            "url": "/cart/",
            "message": "Opening your shopping cart."
        })

    if any(p in cmd_lower for p in ["track order", "track my order", "where is my order", "delivery status", "live track"]):
        return JsonResponse({
            "status": "success",
            "action": "navigate",
            "url": "/orders/",
            "message": "Opening your live order tracking."
        })

    if any(p in cmd_lower for p in ["wallet", "balance", "freshcash", "my money"]):
        return JsonResponse({
            "status": "success",
            "action": "navigate",
            "url": "/wallet/",
            "message": "Opening your FreshCash wallet."
        })

    if any(p in cmd_lower for p in ["smart list", "grocery list", "scanner", "scan list"]):
        return JsonResponse({
            "status": "success",
            "action": "navigate",
            "url": "/cart/scan/",
            "message": "Opening FreshScan smart grocery list."
        })

    if any(p in cmd_lower for p in ["category", "categories", "departments"]):
        return JsonResponse({
            "status": "success",
            "action": "navigate",
            "url": "/categories/",
            "message": "Showing all grocery departments."
        })

    if any(p in cmd_lower for p in ["checkout", "pay now", "buy now"]):
        return JsonResponse({
            "status": "success",
            "action": "navigate",
            "url": "/orders/checkout/",
            "message": "Proceeding to checkout."
        })

    # 2. Add-to-Cart Intent
    add_match = re.match(r'^(?:please\s+)?(?:add|put|buy|order)\s+(.*?)(?:\s+(?:to|in)\s+(?:my\s+)?cart)?$', cmd_lower)
    if add_match or "add" in cmd_lower:
        raw_item = add_match.group(1) if add_match else re.sub(r'^(?:add|buy|order)\s+', '', cmd_lower)
        qty, unit, query = parse_line_quantity_and_query(raw_item)
        if not query:
            query = raw_item

        product, score = find_best_product_match(query)
        if product and score >= 35:
            if request.user.is_authenticated:
                allocated_qty = min(qty, product.stock) if product.stock > 0 else 0
                if allocated_qty > 0:
                    cart_item, created = Cart.objects.get_or_create(
                        user=request.user,
                        product=product,
                        defaults={"quantity": allocated_qty}
                    )
                    if not created:
                        cart_item.quantity = min(cart_item.quantity + allocated_qty, product.stock)
                        cart_item.save()

                    return JsonResponse({
                        "status": "success",
                        "action": "added_to_cart",
                        "product_name": product.name,
                        "quantity": allocated_qty,
                        "price": float(product.final_price),
                        "image_url": product.image.url if product.image else "",
                        "message": f"Added {allocated_qty} × {product.name} to your cart!",
                        "redirect_url": "/cart/"
                    })
                else:
                    return JsonResponse({
                        "status": "warning",
                        "action": "out_of_stock",
                        "message": f"Sorry, {product.name} is currently out of stock."
                    })
            else:
                return JsonResponse({
                    "status": "success",
                    "action": "navigate",
                    "url": f"/products/{product.slug}/",
                    "message": f"Found {product.name}. Please login to add it directly to cart."
                })

    # 3. Product Search Intent (Default)
    clean_query = re.sub(r'^(?:find|search|look for|show me|where is|do you have|give me|i want|please find)\s+', '', cmd_lower)
    clean_query = clean_query.strip()
    if not clean_query:
        clean_query = cmd_lower

    matching_prods = Product.objects.filter(available=True, name__icontains=clean_query)[:4]
    preview_items = [
        {
            "id": p.id,
            "name": p.name,
            "price": float(p.final_price),
            "image": p.image.url if p.image else "",
            "slug": p.slug,
        }
        for p in matching_prods
    ]

    return JsonResponse({
        "status": "success",
        "action": "search",
        "query": clean_query,
        "redirect_url": f"/products/?q={clean_query}",
        "message": f"Searching for '{clean_query}'...",
        "count": len(preview_items),
        "results": preview_items,
    })


def barcode_scanner_view(request):
    """
    FreshBarcode™ Dedicated Camera & Barcode Scanner View.
    Provides live video feed scanner, manual barcode input,
    and a sample test barcode strip for desktop testing.
    """
    sample_products = Product.objects.filter(available=True, barcode__isnull=False).select_related('category')[:8]
    return render(request, "products/barcode_scanner.html", {
        "sample_products": sample_products,
    })


def barcode_lookup_api(request):
    """
    API endpoint to lookup product details by scanned barcode.
    Accepts GET / POST with 'barcode' parameter.
    """
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            barcode = body.get("barcode", "").strip()
        except Exception:
            barcode = request.POST.get("barcode", "").strip()
    else:
        barcode = request.GET.get("barcode", "").strip()

    if not barcode:
        return JsonResponse({"status": "error", "message": "No barcode provided."}, status=400)

    clean_code = barcode.replace(" ", "").replace("-", "")

    # Look up by exact barcode match or fallback
    product = Product.objects.filter(barcode=clean_code, available=True).select_related('category').first()
    if not product and clean_code.isdigit():
        # Fallback: check if matches ID or standard EAN format
        product = Product.objects.filter(id=int(clean_code), available=True).select_related('category').first()
        if not product:
            product = Product.objects.filter(barcode=f"890103{int(clean_code):07d}", available=True).select_related('category').first()

    if not product:
        return JsonResponse({
            "status": "not_found",
            "message": f"No active grocery item found for barcode '{barcode}'."
        }, status=404)

    return JsonResponse({
        "status": "success",
        "product": {
            "id": product.id,
            "name": product.name,
            "slug": product.slug,
            "barcode": product.barcode,
            "category": product.category.name,
            "price": float(product.price),
            "discount_price": float(product.discount_price) if product.discount_price else None,
            "final_price": float(product.final_price),
            "savings": float(product.savings_amount),
            "discount_percent": product.discount_percent,
            "stock": product.stock,
            "in_stock": product.stock > 0,
            "image_url": product.image.url if product.image else "",
            "detail_url": reverse("products:detail", args=[product.slug]),
        }
    })


def barcode_add_to_cart_api(request):
    """
    API endpoint to add a scanned product directly to cart by barcode.
    """
    if not request.user.is_authenticated:
        return JsonResponse({
            "status": "auth_required",
            "message": "Please login to add scanned items directly to your cart.",
            "login_url": reverse("accounts:login")
        }, status=401)

    if request.method == "POST":
        try:
            body = json.loads(request.body)
            barcode = body.get("barcode", "").strip()
            qty = int(body.get("quantity", 1))
        except Exception:
            barcode = request.POST.get("barcode", "").strip()
            qty = int(request.POST.get("quantity", 1))
    else:
        barcode = request.GET.get("barcode", "").strip()
        qty = int(request.GET.get("quantity", 1))

    if not barcode:
        return JsonResponse({"status": "error", "message": "No barcode provided."}, status=400)

    clean_code = barcode.replace(" ", "").replace("-", "")
    product = Product.objects.filter(barcode=clean_code, available=True).first()
    if not product and clean_code.isdigit():
        product = Product.objects.filter(id=int(clean_code), available=True).first()

    if not product:
        return JsonResponse({"status": "not_found", "message": f"Product not found for barcode '{barcode}'."}, status=404)

    if product.stock <= 0:
        return JsonResponse({
            "status": "out_of_stock",
            "message": f"Sorry, {product.name} is currently out of stock."
        }, status=400)

    allocated_qty = min(max(1, qty), product.stock)
    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={"quantity": allocated_qty}
    )
    if not created:
        cart_item.quantity = min(cart_item.quantity + allocated_qty, product.stock)
        cart_item.save()

    return JsonResponse({
        "status": "success",
        "message": f"Added {allocated_qty} × {product.name} to your cart!",
        "product_name": product.name,
        "quantity": cart_item.quantity,
        "price": float(product.final_price),
        "cart_url": reverse("cart:index")
    })
