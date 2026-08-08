from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [

    path(
        "",
        views.index,
        name="index"
    ),

    path(
        "orders/",
        views.orders_list,
        name="orders"
    ),

    path(
        "orders/<int:order_id>/update/",
        views.update_order_status,
        name="update_order"
    ),
]