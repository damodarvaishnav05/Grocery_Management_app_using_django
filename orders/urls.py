from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("", views.my_orders, name="my_orders"),

    path("checkout/", views.checkout, name="checkout"),

    path(
        "success/<int:order_id>/",
        views.success,
        name="success"
    ),

    path(
        "detail/<int:order_id>/",
        views.order_detail,
        name="detail"
    ),

    path(
        "invoice/<int:order_id>/",
        views.download_invoice,
        name="invoice"
    ),

    path(
    "cancel/<int:order_id>/",
    views.cancel_order,
    name="cancel"
    ),

]