from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from orders.models import Order
from wishlist.models import Wishlist

from .forms import (
    LoginForm,
    RegisterForm,
    ProfileForm,
)


# =========================================================
# REGISTER
# =========================================================

def register_view(request):

    if request.user.is_authenticated:
        return redirect("home")

    form = RegisterForm(
        request.POST or None,
        request.FILES or None
    )

    if request.method == "POST":

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Registration successful. Please login."
            )

            return redirect(
                "accounts:login"
            )

    return render(
        request,
        "accounts/register.html",
        {
            "form": form
        }
    )


# =========================================================
# LOGIN
# =========================================================

def login_view(request):

    if request.user.is_authenticated:
        return redirect("home")

    form = LoginForm(
        request,
        data=request.POST or None
    )

    if request.method == "POST":

        if form.is_valid():

            login(
                request,
                form.get_user()
            )

            messages.success(
                request,
                "Welcome back!"
            )

            return redirect("home")

    return render(
        request,
        "accounts/login.html",
        {
            "form": form
        }
    )


# =========================================================
# LOGOUT
# =========================================================

@login_required
def logout_view(request):

    # Remove applied coupon
    request.session.pop("coupon_id", None)

    logout(request)

    return redirect("home")


# =========================================================
# PROFILE
# =========================================================

@login_required
def profile(request):

    orders = Order.objects.filter(
        user=request.user
    )

    total_orders = orders.count()

    total_spent = sum(
        order.total_amount
        for order in orders
        if order.status != Order.CANCELLED
    )

    wishlist_count = Wishlist.objects.filter(
        user=request.user
    ).count()

    return render(
        request,
        "accounts/profile.html",
        {
            "total_orders": total_orders,
            "total_spent": total_spent,
            "wishlist_count": wishlist_count,
        }
    )


# =========================================================
# EDIT PROFILE
# =========================================================

@login_required
def edit_profile(request):

    if request.method == "POST":

        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=request.user
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Profile updated successfully."
            )

            return redirect(
                "accounts:profile"
            )

    else:

        form = ProfileForm(
            instance=request.user
        )

    return render(
        request,
        "accounts/edit_profile.html",
        {
            "form": form
        }
    )