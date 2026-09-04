from django.urls import path
from . import views

app_name = "wallet"

urlpatterns = [
    path("", views.wallet_dashboard, name="dashboard"),
    path("top-up/", views.top_up_wallet, name="top_up"),
    path("pay/<int:order_id>/", views.pay_with_wallet, name="pay_with_wallet"),
]

