from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse

from coupons.models import Coupon
from cart.models import Cart
from .models import Order, OrderItem
from .forms import CheckoutForm

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

@login_required
def checkout(request):

    cart_items = Cart.objects.filter(user=request.user)

    total = sum(item.total_price for item in cart_items)

    discount = Decimal("0.00")

    coupon_id = request.session.get("coupon_id")

    if coupon_id:

        try:
            coupon = Coupon.objects.get(id=coupon_id)

            if total >= coupon.minimum_order_amount:

                discount = (
                    total *
                    Decimal(coupon.discount_percent)
                ) / Decimal("100")

        except Coupon.DoesNotExist:
            pass

    final_total = total - discount

    if request.method == "POST":

        form = CheckoutForm(request.POST)

        if form.is_valid():

            order = Order.objects.create(

                user=request.user,

                full_name=form.cleaned_data["full_name"],

                phone=form.cleaned_data["phone"],

                address=form.cleaned_data["address"],

                city=form.cleaned_data["city"],

                state=form.cleaned_data["state"],

                pincode=form.cleaned_data["pincode"],

                total_amount=final_total

            )

            for item in cart_items:

                OrderItem.objects.create(

                    order=order,

                    product=item.product,

                    quantity=item.quantity,

                    price=item.product.final_price

                )

            cart_items.delete()

            return redirect(
                "payments:payment",
                order.id
            )

    else:

        form = CheckoutForm()

    return render(
        request,
        "orders/checkout.html",
        {
            "form": form,
            "cart_items": cart_items,
            "total": final_total,
            "discount": discount,
        }
    )


@login_required
def success(request, order_id):

    order = Order.objects.get(
        id=order_id,
        user=request.user
    )

    return render(
        request,
        "orders/order_success.html",
        {
            "order": order
        }
    )


@login_required
def my_orders(request):

    orders = Order.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "orders/my_orders.html",
        {
            "orders": orders
        }
    )


@login_required
def order_detail(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    return render(
        request,
        "orders/order_detail.html",
        {
            "order": order
        }
    )

@login_required
def download_invoice(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        f'attachment; filename="invoice_{order.id}.pdf"'
    )

    pdf = SimpleDocTemplate(response)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph("FreshMart", styles["Title"])
    )

    elements.append(
        Paragraph(
            "Grocery Delivery Invoice",
            styles["Heading2"]
        )
    )

    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            f"<b>Invoice No:</b> {order.id}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"<b>Date:</b> {order.created_at.strftime('%d %b %Y')}",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 15))

    elements.append(
        Paragraph(
            "<b>Customer Details</b>",
            styles["Heading3"]
        )
    )

    elements.append(
        Paragraph(order.full_name, styles["Normal"])
    )

    elements.append(
        Paragraph(order.phone, styles["Normal"])
    )

    elements.append(
        Paragraph(order.address, styles["Normal"])
    )

    elements.append(Spacer(1, 20))

    data = [["Product", "Qty", "Price"]]

    for item in order.items.all():

        data.append([
            item.product.name,
            str(item.quantity),
            f"Rs {item.subtotal()}"
        ])

    table = Table(
        data,
        colWidths=[250, 80, 120]
    )

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.green),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ])
    )

    elements.append(table)

    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            f"<b>Grand Total: Rs {order.total_amount}</b>",
            styles["Heading2"]
        )
    )

    elements.append(
        Paragraph(
            f"<b>Status:</b> {order.status}",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 30))

    elements.append(
        Paragraph(
            "Thank you for shopping with FreshMart!",
            styles["Heading3"]
        )
    )

    pdf.build(elements)

    return response


@login_required
def cancel_order(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    if order.status == Order.PENDING:

        # Restore product stock
        for item in order.items.all():

            product = item.product

            product.stock += item.quantity

            product.save()

        # Change order status
        order.status = Order.CANCELLED
        order.save()

        messages.success(
            request,
            "Order cancelled successfully."
        )

    return redirect("orders:my_orders")