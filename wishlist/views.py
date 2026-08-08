from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .models import Wishlist
from products.models import Product


@login_required
def index(request):

    items = Wishlist.objects.filter(user=request.user)

    return render(
        request,
        "wishlist/index.html",
        {
            "items": items
        }
    )


@login_required
def add(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    return redirect("wishlist:index")


@login_required
def remove(request, wishlist_id):

    item = get_object_or_404(
        Wishlist,
        id=wishlist_id,
        user=request.user
    )

    item.delete()

    return redirect("wishlist:index")