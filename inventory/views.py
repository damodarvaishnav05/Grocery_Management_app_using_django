from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from django.shortcuts import render
from products.models import Product
from .models import InventoryHistory


@staff_member_required
def index(request):
    """
    Inventory Management and Stock Audit Dashboard
    """
    products = Product.objects.all().select_related("category").order_by("stock")
    total_products = products.count()
    total_stock = products.aggregate(Sum("stock"))["stock__sum"] or 0
    low_stock = products.filter(stock__gt=0, stock__lt=10)
    out_of_stock = products.filter(stock=0)

    recent_history = InventoryHistory.objects.select_related("product").order_by("-created_at")[:25]

    return render(
        request,
        "inventory/index.html",
        {
            "products": products,
            "total_products": total_products,
            "total_stock": total_stock,
            "low_stock": low_stock,
            "out_of_stock": out_of_stock,
            "recent_history": recent_history,
        }
    )
