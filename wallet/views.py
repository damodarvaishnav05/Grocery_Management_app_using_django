from decimal import Decimal
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from inventory.models import InventoryHistory
from orders.models import Order
from payments.models import Payment
from .forms import TopUpWalletForm
from .models import Wallet, WalletTransaction


@login_required
def wallet_dashboard(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    form = TopUpWalletForm()

    # Calculate quick statistics
    all_trxs = wallet.transactions.all()
    total_spent = sum(t.amount for t in all_trxs if t.transaction_type == WalletTransaction.DEBIT)
    total_recharged = sum(t.amount for t in all_trxs if t.transaction_type == WalletTransaction.CREDIT)
    total_refunds = sum(t.amount for t in all_trxs if t.transaction_type == WalletTransaction.REFUND)

    # Filter type if requested
    trx_type = request.GET.get("type")
    if trx_type in ["CREDIT", "DEBIT", "REFUND"]:
        all_trxs = all_trxs.filter(transaction_type=trx_type)

    paginator = Paginator(all_trxs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "wallet/index.html",
        {
            "wallet": wallet,
            "form": form,
            "transactions": page_obj,
            "total_spent": total_spent,
            "total_recharged": total_recharged,
            "total_refunds": total_refunds,
            "current_filter": trx_type,
        }
    )


@login_required
def top_up_wallet(request):
    if request.method != "POST":
        return redirect("wallet:dashboard")

    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    form = TopUpWalletForm(request.POST)

    redirect_url = request.POST.get("next") or request.GET.get("next") or "wallet:dashboard"

    if form.is_valid():
        amount = form.cleaned_data["amount"]
        try:
            wallet.credit(
                amount=amount,
                description="Instant UPI / Card Top-Up",
                reference_id=f"TOPUP-{request.user.id}-{int(amount)}"
            )
            messages.success(
                request,
                f"🎉 ₹{amount:.2f} successfully credited to your FreshMart Wallet! Current balance: ₹{wallet.balance:.2f}"
            )
        except Exception as e:
            messages.error(request, f"Top-up error: {str(e)}")
    else:
        messages.error(request, "Please enter a valid amount between ₹10 and ₹10,000.")

    if redirect_url.startswith("/"):
        return redirect(redirect_url)
    return redirect(redirect_url)


@login_required
def pay_with_wallet(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status == Order.CONFIRMED:
        messages.info(request, "This order has already been paid and confirmed.")
        return redirect("orders:success", order.id)

    wallet, _ = Wallet.objects.get_or_create(user=request.user)

    if wallet.balance < order.total_amount:
        diff = order.total_amount - wallet.balance
        messages.warning(
            request,
            f"Insufficient wallet balance. You need ₹{diff:.2f} more to pay with FreshMart Wallet."
        )
        return redirect("payments:payment", order.id)

    try:
        with transaction.atomic():
            # 1. Debit Wallet
            wallet.debit(
                amount=order.total_amount,
                description=f"1-Click Payment for Order #{order.id}",
                reference_id=f"ORDER-{order.id}"
            )

            # 2. Record/Update Payment
            payment, _ = Payment.objects.get_or_create(
                order=order,
                defaults={"amount": order.total_amount}
            )
            payment.status = Payment.SUCCESS
            payment.razorpay_order_id = f"wallet_pay_{order.id}"
            payment.save()

            # 3. Confirm Order
            order.status = Order.CONFIRMED
            order.save()

            # 4. Decrement product stock & record inventory history
            for item in order.items.all():
                prod = item.product
                if prod.stock >= item.quantity:
                    prod.stock -= item.quantity
                else:
                    prod.stock = 0
                prod.save()

                InventoryHistory.objects.create(
                    product=prod,
                    action=InventoryHistory.STOCK_OUT,
                    quantity=item.quantity,
                    note=f"Wallet 1-Click Order #{order.id}"
                )

            # 5. Send Email Confirmation
            if request.user.email:
                send_mail(
                    subject=f"Order #{order.id} Confirmed (Paid via FreshMart Wallet)",
                    message=f"""
Hello {order.full_name},

Thank you for your order! Payment of ₹{order.total_amount} was successfully processed via your FreshMart Wallet.

Order ID: #{order.id}
Delivery Address: {order.address}, {order.city} - {order.pincode}
Remaining Wallet Balance: ₹{wallet.balance}

FreshMart express delivery will arrive in 10-15 minutes!
""",
                    from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "FreshMart <noreply@freshmart.com>"),
                    recipient_list=[request.user.email],
                    fail_silently=True
                )

        messages.success(
            request,
            f"⚡ Instant 1-Click Payment Successful! ₹{order.total_amount} debited from your FreshMart Wallet."
        )
        return redirect("orders:success", order.id)

    except Exception as e:
        messages.error(request, f"Transaction failed: {str(e)}")
        return redirect("payments:payment", order.id)
