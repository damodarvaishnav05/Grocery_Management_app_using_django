from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from coupons.models import Coupon
from products.models import Product
from .models import Cart
from .scanner import parse_and_match_grocery_list


@login_required
def index(request):

    cart_items = Cart.objects.filter(user=request.user)

    subtotal = sum(item.total_price for item in cart_items)

    discount = Decimal("0.00")

    coupon_id = request.session.get("coupon_id")

    if coupon_id:
        try:
            coupon = Coupon.objects.get(id=coupon_id)

            if subtotal >= coupon.minimum_order_amount:
                discount = (
                    subtotal *
                    Decimal(coupon.discount_percent)
                ) / Decimal("100")

        except Coupon.DoesNotExist:
            pass

    total = subtotal - discount

    return render(
        request,
        "cart/index.html",
        {
            "cart_items": cart_items,
            "subtotal": subtotal,
            "discount": discount,
            "total": total,
        },
    )


@login_required
def add_to_cart(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    if product.stock <= 0:
        return redirect("products:index")

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product,
    )

    if created:
        cart_item.quantity = 1

    else:

        if cart_item.quantity >= product.stock:
            return redirect("cart:index")

        cart_item.quantity += 1

    cart_item.save()

    return redirect("cart:index")


@login_required
def increase_quantity(request, cart_id):

    item = get_object_or_404(
        Cart,
        id=cart_id,
        user=request.user
    )

    if item.quantity < item.product.stock:
        item.quantity += 1
        item.save()

    return redirect("cart:index")


@login_required
def decrease_quantity(request, cart_id):

    item = get_object_or_404(
        Cart,
        id=cart_id,
        user=request.user
    )

    if item.quantity > 1:
        item.quantity -= 1
        item.save()

    else:
        item.delete()

    return redirect("cart:index")


@login_required
def remove_item(request, cart_id):

    item = get_object_or_404(
        Cart,
        id=cart_id,
        user=request.user
    )

    item.delete()

    return redirect("cart:index")


@login_required
def smart_scanner(request):
    """
    Renders the FreshScan AI Grocery List Scanner interface and processes text or OCR input
    """
    raw_text = ""
    scan_results = None

    if request.method == "POST":
        raw_text = request.POST.get("grocery_text", "").strip()
        if raw_text:
            scan_results = parse_and_match_grocery_list(raw_text)

        if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.GET.get("format") == "json":
            if scan_results:
                matches_data = [
                    {
                        "product_id": m["product"].id,
                        "product_name": m["product"].name,
                        "product_image": m["product"].image.url if m["product"].image else "",
                        "product_price": float(m["product"].final_price),
                        "unit_price": float(m["product"].price),
                        "requested_quantity": m["requested_quantity"],
                        "allocated_quantity": m["allocated_quantity"],
                        "stock": m["product"].stock,
                        "in_stock": m["in_stock"],
                        "confidence": m["confidence"],
                        "subtotal": float(m["subtotal"]),
                        "original_line": m["original_line"],
                    }
                    for m in scan_results["matches"]
                ]
                return JsonResponse({
                    "status": "success",
                    "total_items": scan_results["total_items"],
                    "matched_count": scan_results["matched_count"],
                    "estimated_total": float(scan_results["estimated_total"]),
                    "matches": matches_data,
                    "unmatched": scan_results["unmatched"],
                })
            return JsonResponse({"status": "empty", "matches": [], "unmatched": []})

    return render(
        request,
        "cart/smart_scan.html",
        {
            "raw_text": raw_text,
            "scan_results": scan_results,
        }
    )


@login_required
def batch_add_to_cart(request):
    """
    1-Click batch adding of all approved matched products from the grocery list
    """
    if request.method != "POST":
        return redirect("cart:smart_scan")

    selected_ids = request.POST.getlist("selected_products")
    if not selected_ids:
        messages.warning(request, "No items were selected to add.")
        return redirect("cart:smart_scan")

    added_count = 0
    with transaction.atomic():
        for pid_str in selected_ids:
            try:
                pid = int(pid_str)
                product = Product.objects.get(id=pid, available=True)
                qty = int(request.POST.get(f"quantity_{pid}", 1))
                qty = max(1, min(qty, product.stock))

                cart_item, created = Cart.objects.get_or_create(
                    user=request.user,
                    product=product,
                    defaults={"quantity": qty}
                )
                if not created:
                    cart_item.quantity = min(cart_item.quantity + qty, product.stock)
                    cart_item.save()

                added_count += 1
            except (ValueError, Product.DoesNotExist):
                continue

    if added_count > 0:
        messages.success(
            request,
            f"✨ FreshScan added {added_count} items from your grocery list into your cart!"
        )
    return redirect("cart:index")