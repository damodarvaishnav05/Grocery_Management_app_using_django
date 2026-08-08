from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404

from products.models import Product
from orders.models import Order

User = get_user_model()


@staff_member_required
def index(request):

    total_products = Product.objects.count()

    total_customers = User.objects.filter(
        is_staff=False
    ).count()

    total_orders = Order.objects.count()

    revenue = (
        Order.objects.filter(
            status=Order.DELIVERED
        ).aggregate(
            Sum("total_amount")
        )["total_amount__sum"]
        or 0
    )

    pending_orders = Order.objects.exclude(
        status=Order.DELIVERED
    ).count()

    delivered_orders = Order.objects.filter(
        status=Order.DELIVERED
    ).count()

    low_stock_products = Product.objects.filter(
        stock__lt=10
    )

    low_stock_count = Product.objects.filter(
    stock__lt=5
    ).count()

    recent_orders = Order.objects.order_by(
        "-created_at"
    )[:10]

    return render(
        request,
        "dashboard/index.html",
        {
            "total_products": total_products,
            "total_customers": total_customers,
            "total_orders": total_orders,
            "revenue": revenue,
            "pending_orders": pending_orders,
            "delivered_orders": delivered_orders,
            "low_stock_products": low_stock_products,
            "recent_orders": recent_orders,
            "low_stock_count": low_stock_count,
        }
    )


@staff_member_required
def orders_list(request):

    orders = Order.objects.all().order_by(
        "-created_at"
    )

    return render(
        request,
        "dashboard/orders.html",
        {
            "orders": orders
        }
    )


@staff_member_required
def update_order_status(
    request,
    order_id
):

    order = get_object_or_404(
        Order,
        id=order_id
    )

    if request.method == "POST":

        status = request.POST.get(
            "status"
        )

        order.status = status
        order.save()

    return redirect(
        "dashboard:orders"
    )