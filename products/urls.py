from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    path("", views.index, name="index"),
    path("scanner/", views.barcode_scanner_view, name="barcode_scanner"),
    path("api/voice-command/", views.voice_command_api, name="voice_command_api"),
    path("api/barcode-lookup/", views.barcode_lookup_api, name="barcode_lookup_api"),
    path("api/barcode-add-to-cart/", views.barcode_add_to_cart_api, name="barcode_add_to_cart_api"),
    path("<slug:slug>/", views.detail, name="detail"),
]
