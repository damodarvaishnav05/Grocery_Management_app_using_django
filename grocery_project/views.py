from django.shortcuts import render
from products.models import Product
from categories.models import Category
from django.contrib.auth import get_user_model
from datetime import date


User = get_user_model()

def home(request):

    if Product.objects.count() < 10:
        try:
            from products.seed import seed_all_groceries
            seed_all_groceries()
        except Exception:
            pass

    categories = Category.objects.filter(is_active=True)
    featured_products = Product.objects.filter(available=True)[:8]
    season_best = (
        Product.objects.filter(available=True, name__icontains="apple").first()
        or Product.objects.filter(available=True).order_by("-average_rating").first()
    )

    context = {
        "categories": categories,
        "featured_products": featured_products,
        "season_best": season_best,
        "product_count": Product.objects.count(),
        "category_count": categories.count(),
        "customer_count": User.objects.filter(is_staff=False).count(),
        "today_coupon": f"OMSUPER{date.today().strftime('%d%m')}",
    }

    return render(
        request,
        "home.html",
        context
    )