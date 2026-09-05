from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from coupons.models import Coupon
from orders.models import Order
from .models import Payment
from inventory.models import InventoryHistory
import razorpay
from django.conf import settings
from django.core.mail import send_mail
from django.conf import settings

@login_required
def payment(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    payment, created = Payment.objects.get_or_create(
        order=order,
        defaults={
            "amount": order.total_amount
        }
    )

    razorpay_amount = int(order.total_amount * 100)
    razorpay_order_id = f"order_{order.id}"

    if settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET:
        try:
            client = razorpay.Client(
                auth=(
                    settings.RAZORPAY_KEY_ID,
                    settings.RAZORPAY_KEY_SECRET
                )
            )

            razorpay_order = client.order.create({
                "amount": max(100, razorpay_amount),
                "currency": "INR",
                "payment_capture": 1
            })
            razorpay_order_id = razorpay_order.get("id", razorpay_order_id)
        except Exception:
            # Fallback for development/demo when Razorpay keys are not configured
            pass

    payment.razorpay_order_id = razorpay_order_id
    payment.save()

    return render(
        request,
        "payments/payment.html",
        {
            "order": order,
            "payment": payment,
            "razorpay_order_id": razorpay_order_id,
            "razorpay_key": settings.RAZORPAY_KEY_ID,
            "razorpay_amount": razorpay_amount,
        }
    )


@login_required
def payment_success(request, payment_id):

    payment = get_object_or_404(
        Payment,
        id=payment_id
    )

    if payment.status == Payment.SUCCESS:
        return redirect(
            "orders:success",
            payment.order.id
        )

    payment.status = Payment.SUCCESS
    payment.save()

    order = payment.order

    order.status = Order.CONFIRMED
    order.save()

    if request.user.email:

        send_mail(
            subject=f"Order #{order.id} Confirmed",

            message=f"""
    Hello {order.full_name},

    Your order has been confirmed.

    Order ID: {order.id}
    Amount: ₹{order.total_amount}

    Thank you for shopping with Om Super Mart.
    """,

            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "Om Super Mart <noreply@omsupermart.com>"),

            recipient_list=[request.user.email],

            fail_silently=True,
        )

    # Reduce stock
    for item in order.items.all():

        product = item.product

        product.stock -= item.quantity

        if product.stock < 0:
            product.stock = 0

        product.save()

        InventoryHistory.objects.create(
            product=product,
            action=InventoryHistory.STOCK_OUT,
            quantity=item.quantity,
            note=f"Order #{order.id}"
        )

    # Update coupon usage
    coupon_id = request.session.get("coupon_id")

    if coupon_id:

        try:
            coupon = Coupon.objects.get(id=coupon_id)

            coupon.used_count += 1
            coupon.save()

            del request.session["coupon_id"]

        except Coupon.DoesNotExist:
            pass

    return redirect(
        "orders:success",
        order.id
    )


@login_required
def payment_failed(request, payment_id):

    payment = get_object_or_404(
        Payment,
        id=payment_id
    )

    payment.status = Payment.FAILED
    payment.save()

    return render(
        request,
        "payments/payment_failed.html",
        {
            "payment": payment
        }
    )