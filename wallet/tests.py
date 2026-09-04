from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from categories.models import Category
from orders.models import Order, OrderItem
from products.models import Product
from wallet.models import Wallet, WalletTransaction

User = get_user_model()


class WalletModelAndSignalTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="walletuser",
            password="securepassword123",
            email="walletuser@example.com"
        )

    def test_wallet_auto_created_via_signal(self):
        self.assertTrue(hasattr(self.user, "wallet"))
        self.assertEqual(self.user.wallet.balance, Decimal("0.00"))
        self.assertTrue(self.user.wallet.is_active)

    def test_credit_and_debit_operations(self):
        wallet = self.user.wallet

        # Credit
        trx = wallet.credit(Decimal("500.00"), description="Test Credit")
        wallet.refresh_from_db()
        self.assertEqual(wallet.balance, Decimal("500.00"))
        self.assertEqual(trx.transaction_type, WalletTransaction.CREDIT)
        self.assertEqual(trx.balance_after, Decimal("500.00"))

        # Debit
        trx_debit = wallet.debit(Decimal("150.00"), description="Test Debit")
        wallet.refresh_from_db()
        self.assertEqual(wallet.balance, Decimal("350.00"))
        self.assertEqual(trx_debit.transaction_type, WalletTransaction.DEBIT)
        self.assertEqual(trx_debit.balance_after, Decimal("350.00"))

    def test_insufficient_balance_debit_raises_error(self):
        wallet = self.user.wallet
        with self.assertRaises(Exception):
            wallet.debit(Decimal("100.00"))


class WalletViewsAndPaymentTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="shopper1",
            password="password123",
            email="shopper1@example.com"
        )
        self.category = Category.objects.create(name="Beverages", slug="beverages", is_active=True)
        self.product = Product.objects.create(
            category=self.category,
            name="Orange Juice",
            slug="orange-juice",
            price=Decimal("100.00"),
            stock=10,
            available=True
        )

    def test_wallet_dashboard_view(self):
        self.client.login(username="shopper1", password="password123")
        response = self.client.get(reverse("wallet:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "FreshMart Cash & Wallet")
        self.assertContains(response, "Recharge Wallet")

    def test_wallet_top_up_view(self):
        self.client.login(username="shopper1", password="password123")
        response = self.client.post(
            reverse("wallet:top_up"),
            {"amount": "250.00"}
        )
        self.assertEqual(response.status_code, 302)
        self.user.wallet.refresh_from_db()
        self.assertEqual(self.user.wallet.balance, Decimal("250.00"))

    def test_pay_with_wallet_success(self):
        self.client.login(username="shopper1", password="password123")
        self.user.wallet.credit(Decimal("500.00"))

        order = Order.objects.create(
            user=self.user,
            full_name="Shopper One",
            phone="9988776655",
            address="456 Market Road",
            city="Pune",
            state="MH",
            pincode="411045",
            total_amount=Decimal("100.00"),
            status=Order.PENDING
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=1,
            price=Decimal("100.00")
        )

        response = self.client.post(reverse("wallet:pay_with_wallet", args=[order.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("orders:success", args=[order.id]))

        order.refresh_from_db()
        self.assertEqual(order.status, Order.CONFIRMED)

        self.user.wallet.refresh_from_db()
        self.assertEqual(self.user.wallet.balance, Decimal("400.00"))

        # Inventory check
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 9)

    def test_pay_with_wallet_insufficient_funds(self):
        self.client.login(username="shopper1", password="password123")
        # Wallet balance is 0.00

        order = Order.objects.create(
            user=self.user,
            full_name="Shopper One",
            phone="9988776655",
            address="456 Market Road",
            city="Pune",
            state="MH",
            pincode="411045",
            total_amount=Decimal("100.00"),
            status=Order.PENDING
        )

        response = self.client.post(reverse("wallet:pay_with_wallet", args=[order.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("payments:payment", args=[order.id]))

        order.refresh_from_db()
        self.assertEqual(order.status, Order.PENDING)
