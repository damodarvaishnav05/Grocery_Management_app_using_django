from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from coupons.models import Coupon
from products.models import Product
from .models import Cart


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