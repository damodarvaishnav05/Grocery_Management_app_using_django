from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "barcode",
        "category",
        "price",
        "stock",
        "available",
    )

    list_filter = (
        "category",
        "available",
    )

    search_fields = (
        "name",
        "barcode",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }