from django.shortcuts import render
from .models import Category


def index(request):
    categories = Category.objects.all()

    return render(
        request,
        "categories/index.html",
        {
            "categories": categories
        }
    )