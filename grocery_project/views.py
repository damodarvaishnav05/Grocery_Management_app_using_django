from django.shortcuts import render
from products.models import Product
from categories.models import Category
from django.contrib.auth import get_user_model
from datetime import date


User = get_user_model()

def home(request):

    categories = Category.objects.all()

    context = {
        "categories": categories,
        "product_count": Product.objects.count(),
        "category_count": categories.count(),
        "customer_count": User.objects.filter(is_staff=False).count(),
        "today_coupon": f"FRESH{date.today().strftime('%d%m')}",
    }

    return render(
        request,
        "home.html",
        context
    )