from django.shortcuts import render, get_object_or_404
from django.db.models import Avg
from django.core.paginator import Paginator

from .models import Product
from reviews.models import Review
from reviews.forms import ReviewForm
from categories.models import Category



def index(request):

    # Get available products
    products = Product.objects.filter(
        available=True
    )


    # Get all categories
    categories = Category.objects.all()


    # Search
    query = request.GET.get("q")

    if query:

        products = products.filter(
            name__icontains=query
        )


    # Category filter
    category_slug = request.GET.get("category")

    if category_slug:

        products = products.filter(
            category__slug=category_slug
        )



    paginator = Paginator(
        products,
        12
    )

    page_number = request.GET.get("page")

    products = paginator.get_page(
        page_number
    )



    context = {

        "products": products,

        "categories": categories,

        "query": query,

    }


    return render(
        request,
        "products/index.html",
        context
    )




def detail(request, slug):

    # Get product
    product = get_object_or_404(
        Product,
        slug=slug,
        available=True
    )


    # Get reviews
    reviews = product.reviews.all()


    # Calculate average rating
    average_rating = reviews.aggregate(
        Avg("rating")
    )["rating__avg"]


    # Get related products
    related_products = Product.objects.filter(
        category=product.category,
        available=True
    ).exclude(
        id=product.id
    )[:4]


    # Review form
    form = ReviewForm()


    # Context
    context = {

        "product": product,

        "reviews": reviews,

        "average_rating": average_rating,

        "related_products": related_products,

        "form": form,

    }


    return render(
        request,
        "products/detail.html",
        context
    )