def common_data(request):
    """
    Context processor to provide cart item count and wishlist count
    to all templates when user is authenticated.
    """
    if request.user.is_authenticated:
        try:
            from cart.models import Cart
            from wishlist.models import Wishlist
            from wallet.models import Wallet
            cart_count = Cart.objects.filter(user=request.user).count()
            wishlist_count = Wishlist.objects.filter(user=request.user).count()
            wallet, _ = Wallet.objects.get_or_create(user=request.user)
            wallet_balance = wallet.balance
        except Exception:
            cart_count = 0
            wishlist_count = 0
            wallet_balance = 0
    else:
        cart_count = 0
        wishlist_count = 0
        wallet_balance = 0

    return {
        "cart_count": cart_count,
        "wishlist_count": wishlist_count,
        "wallet_balance": wallet_balance,
    }

