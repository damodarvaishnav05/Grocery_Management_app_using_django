from django.contrib import admin
from .models import Order, OrderItem, OrderDeliveryTracking


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "price", "subtotal")


class OrderDeliveryTrackingInline(admin.StackedInline):
    model = OrderDeliveryTracking
    can_delete = False
    extra = 0
    fields = (
        ("dark_store_name", "dark_store_address"),
        ("dark_store_lat", "dark_store_lng"),
        ("customer_lat", "customer_lng"),
        ("rider_name", "rider_phone", "rider_vehicle"),
        ("rider_rating", "delivery_pin", "override_stage"),
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "total_amount",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "id",
        "user__username",
        "full_name",
        "phone",
        "city",
        "pincode",
    )

    inlines = [OrderItemInline, OrderDeliveryTrackingInline]


@admin.register(OrderDeliveryTracking)
class OrderDeliveryTrackingAdmin(admin.ModelAdmin):

    list_display = (
        "order",
        "rider_name",
        "rider_vehicle",
        "delivery_pin",
        "override_stage",
        "updated_at",
    )

    list_filter = (
        "override_stage",
        "rider_name",
    )

    search_fields = (
        "order__id",
        "rider_name",
        "delivery_pin",
    )