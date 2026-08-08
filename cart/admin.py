from django.contrib import admin
from .models import Cart


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "product",
        "quantity",
        "total_price",
    )

    search_fields = (
        "user__username",
        "product__name",
    )