def common_data(request):
    """
    Context processor to provide cart item count and wishlist count
    to all templates when user is authenticated.
    """
    sidebar_cart_items = []
    sidebar_cart_total = 0
    sidebar_recent_orders = []
    user_referral_code = ""

    if request.user.is_authenticated:
        try:
            from cart.models import Cart
            from wishlist.models import Wishlist
            from wallet.models import Wallet
            from orders.models import Order

            cart_qs = Cart.objects.filter(user=request.user).select_related("product")
            cart_count = cart_qs.count()
            wishlist_count = Wishlist.objects.filter(user=request.user).count()

            # Process sidebar cart items
            items_list = []
            total = 0
            for item in cart_qs[:4]:  # Show top items in right sidebar
                line_total = item.product.final_price * item.quantity
                total += line_total
                items_list.append({
                    "id": item.id,
                    "product": item.product,
                    "quantity": item.quantity,
                    "line_total": line_total,
                })
            sidebar_cart_items = items_list
            sidebar_cart_total = total

            wallet, _ = Wallet.objects.get_or_create(user=request.user)
            wallet_balance = wallet.balance
            user_referral_code = request.user.referral_code or ""

            sidebar_recent_orders = Order.objects.filter(user=request.user).order_by("-created_at")[:2]
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
        "sidebar_cart_items": sidebar_cart_items,
        "sidebar_cart_total": sidebar_cart_total,
        "sidebar_recent_orders": sidebar_recent_orders,
        "user_referral_code": user_referral_code,
        "delivery_location": "Indore, Madhya Pradesh 452001",
    }

