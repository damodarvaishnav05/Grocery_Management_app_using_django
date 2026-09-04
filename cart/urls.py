from django.urls import path
from . import views

app_name = "cart"

urlpatterns = [
    path("", views.index, name="index"),

    path(
        "add/<int:product_id>/",
        views.add_to_cart,
        name="add"
    ),

    path(
        "increase/<int:cart_id>/",
        views.increase_quantity,
        name="increase_quantity"
    ),

    path(
        "decrease/<int:cart_id>/",
        views.decrease_quantity,
        name="decrease_quantity"
    ),

    path(
        "remove/<int:cart_id>/",
        views.remove_item,
        name="remove_item"
    ),

    path(
        "scan/",
        views.smart_scanner,
        name="smart_scan"
    ),
    path(
        "batch-add/",
        views.batch_add_to_cart,
        name="batch_add"
    ),
]