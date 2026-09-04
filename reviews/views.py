from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404

from products.models import Product
from .models import Review
from .forms import ReviewForm


@login_required
def add_review(request, slug):

    product = get_object_or_404(Product, slug=slug)

    review, created = Review.objects.get_or_create(
        product=product,
        user=request.user
    )

    if request.method == "POST":

        form = ReviewForm(
            request.POST,
            instance=review
        )

        if form.is_valid():

            form.save()

    return redirect("products:detail", slug=slug)


@login_required
def add_review_by_id(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return add_review(request, product.slug)