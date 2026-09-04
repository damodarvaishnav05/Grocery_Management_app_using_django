from decimal import Decimal
from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone
from datetime import timedelta

from .models import Coupon
def create_daily_coupon():

    today = timezone.now().date()

    code = f"FRESH{today.strftime('%d%m')}"

    coupon, created = Coupon.objects.get_or_create(
        code=code,
        defaults={
            "discount_percent": 10,
            "minimum_order_amount": 0,
            "active": True,
            "valid_from": timezone.now(),
            "valid_to": timezone.now() + timedelta(days=1),
            "usage_limit": 1000,
        }
    )

    return coupon

def apply_coupon(request):

    code = request.POST.get("coupon_code")

    if not code:
        messages.error(request, "Coupon code required")
        return redirect("cart:index")

    create_daily_coupon()

    try:
        coupon = Coupon.objects.get(
            code__iexact=code,
            active=True
        )

    except Coupon.DoesNotExist:
        messages.error(request, "Invalid coupon")
        return redirect("cart:index")

    now = timezone.now()

    if now < coupon.valid_from or now > coupon.valid_to:
        messages.error(request, "Coupon expired")
        return redirect("cart:index")

    if coupon.used_count >= coupon.usage_limit:
        messages.error(request, "Coupon usage limit reached")
        return redirect("cart:index")

    request.session["coupon_id"] = coupon.id

    messages.success(request, f"Coupon '{coupon.code}' applied! ({coupon.discount_percent}% OFF)")

    return redirect("cart:index")


def remove_coupon(request):

    if "coupon_id" in request.session:
        del request.session["coupon_id"]
        messages.info(request, "Coupon removed from order.")

    return redirect("cart:index")


