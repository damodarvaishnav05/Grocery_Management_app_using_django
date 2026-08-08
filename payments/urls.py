from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [

    path(
        "<int:order_id>/",
        views.payment,
        name="payment"
    ),

    path(
        "success/<int:payment_id>/",
        views.payment_success,
        name="success"
    ),

    path(
        "failed/<int:payment_id>/",
        views.payment_failed,
        name="failed"
    ),

]