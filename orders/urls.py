from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("", views.my_orders, name="my_orders"),
    path("list/", views.my_orders, name="index"),

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
        "invoice/<int:order_id>/pdf/",
        views.download_invoice,
        name="download_invoice"
    ),

    path(
        "cancel/<int:order_id>/",
        views.cancel_order,
        name="cancel"
    ),

    path(
        "track/<int:order_id>/",
        views.track_order,
        name="track"
    ),
    path(
        "api/track/<int:order_id>/",
        views.order_tracking_api,
        name="api_track"
    ),
    path(
        "api/track/<int:order_id>/update-location/",
        views.update_live_location_api,
        name="update_location"
    ),
    path(
        "api/track/<int:order_id>/simulate/<str:stage>/",
        views.simulate_tracking_stage,
        name="simulate_track"
    ),

]
