"""
URL configuration for grocery_project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from django.views.generic import TemplateView
from .views import home, custom_500_handler, custom_404_handler

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', home, name='home'),
    path('offline/', TemplateView.as_view(template_name='offline.html'), name='offline'),

    path('accounts/', include('accounts.urls')),
    path('categories/', include('categories.urls')),
    path('products/', include('products.urls')),
    path('cart/', include('cart.urls')),
    path('wishlist/', include('wishlist.urls')),
    path('orders/', include('orders.urls')),
    path('payments/', include('payments.urls')),
    path('inventory/', include('inventory.urls')),
    path('reviews/', include('reviews.urls')),
    path('coupons/', include('coupons.urls')),
    path('ai/', include('ai_assistant.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('wallet/', include('wallet.urls')),
    path("accounts/", include("allauth.urls")),
]

from django.views.static import serve
from django.urls import re_path

static_dir = (
    settings.STATIC_ROOT
    if (settings.STATIC_ROOT.exists() and any(settings.STATIC_ROOT.iterdir()))
    else (settings.BASE_DIR / "static")
)

urlpatterns += [
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': static_dir}),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

handler500 = "grocery_project.views.custom_500_handler"
handler404 = "grocery_project.views.custom_404_handler"
