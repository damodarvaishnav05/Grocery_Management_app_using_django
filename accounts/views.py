import os
import logging
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

logger = logging.getLogger(__name__)


def is_google_auth_configured():
    cid = os.getenv("GOOGLE_CLIENT_ID", "").strip()
    sec = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()
    if cid and sec and cid != "not-configured" and sec != "not-configured":
        return True
    try:
        from allauth.socialaccount.models import SocialApp
        app = SocialApp.objects.filter(provider="google").first()
        if (
            app
            and app.client_id
            and app.client_id != "not-configured"
            and app.secret
            and app.secret != "not-configured"
        ):
            return True
    except Exception:
        pass
    return False


def google_login_dispatch(request):
    """
    Safely dispatches Google OAuth login.
    If GOOGLE_CLIENT_ID is not configured in Render environment or DB,
    gracefully warns the user without redirecting to Google's Error 401: invalid_client page.
    """
    if not is_google_auth_configured():
        messages.info(
            request,
            "Google Sign-In is not yet configured on this server. Please enter your Username/Email and Password below."
        )
        return redirect("accounts:login")

    try:
        from allauth.socialaccount.providers.google.views import oauth2_login
        return oauth2_login(request)
    except Exception as e:
        logger.warning(f"Error invoking allauth google oauth2_login: {e}")
        messages.warning(
            request,
            "Google Sign-In could not be started. Please use your Username/Email and Password."
        )
        return redirect("accounts:login")


# =========================================================
# REGISTER
# =========================================================

def register_view(request):

    if request.user.is_authenticated:
        return redirect("home")

    ref_code = request.GET.get("ref", "").strip().upper()
    initial_data = {}
    if ref_code:
        initial_data["referral_code"] = ref_code

    form = RegisterForm(
        request.POST or None,
        request.FILES or None,
        initial=initial_data
    )

    if request.method == "POST":

        if form.is_valid():

            user = form.save()

            if user.referred_by:
                try:
                    from wallet.models import Wallet
                    # Welcome bonus for new user
                    user_wallet, _ = Wallet.objects.get_or_create(user=user)
                    user_wallet.credit(
                        50,
                        description=f"Welcome Bonus: Referred by {user.referred_by.username}",
                        reference_id=f"REF-BONUS-{user.id}"
                    )
                    # Reward for referrer
                    referrer_wallet, _ = Wallet.objects.get_or_create(user=user.referred_by)
                    referrer_wallet.credit(
                        50,
                        description=f"Referral Reward: {user.username} joined",
                        reference_id=f"REF-REWARD-{user.id}"
                    )
                    messages.success(
                        request,
                        "Registration successful! ₹50 OmCash welcome reward credited to your wallet. Please login."
                    )
                except Exception:
                    messages.success(
                        request,
                        "Registration successful. Please login."
                    )
            else:
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
            "form": form,
            "is_google_configured": is_google_auth_configured(),
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
            "form": form,
            "is_google_configured": is_google_auth_configured(),
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


# =========================================================
# REFER & EARN
# =========================================================

@login_required
def refer_and_earn_view(request):
    user = request.user
    referral_code = user.referral_code
    if not referral_code:
        referral_code = user.generate_unique_referral_code()
        user.referral_code = referral_code
        user.save()

    referral_link = request.build_absolute_uri(f"/accounts/register/?ref={referral_code}")
    referred_friends = user.referrals.all().order_by("-created_at")
    total_earned = referred_friends.count() * 50

    return render(
        request,
        "accounts/refer.html",
        {
            "referral_code": referral_code,
            "referral_link": referral_link,
            "referred_friends": referred_friends,
            "friends_count": referred_friends.count(),
            "total_earned": total_earned,
        }
    )
