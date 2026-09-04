from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from categories.models import Category
from products.models import Product
from cart.models import Cart
from orders.models import Order, OrderItem
from inventory.models import InventoryHistory

User = get_user_model()


class OrderAndCartTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testshopper",
            password="testpassword123",
            email="shopper@example.com"
        )
        self.category = Category.objects.create(name="Dairy", slug="dairy", is_active=True)
        self.product = Product.objects.create(
            category=self.category,
            name="Organic Cow Milk",
            slug="organic-cow-milk",
            price=Decimal("60.00"),
            stock=15,
            available=True
        )

    def test_checkout_redirects_if_cart_is_empty(self):
        self.client.login(username="testshopper", password="testpassword123")
        response = self.client.get(reverse("orders:checkout"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("cart:index"))

    def test_cancel_order_restores_stock_only_if_confirmed(self):
        self.client.login(username="testshopper", password="testpassword123")

        # Create confirmed order
        order = Order.objects.create(
            user=self.user,
            full_name="Test Shopper",
            phone="9876543210",
            address="123 Fresh Lane",
            city="Pune",
            state="Maharashtra",
            pincode="411001",
            total_amount=Decimal("120.00"),
            status=Order.CONFIRMED
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=2,
            price=Decimal("60.00")
        )

        initial_stock = self.product.stock  # 15
        response = self.client.get(reverse("orders:cancel", args=[order.id]))
        self.assertEqual(response.status_code, 302)

        order.refresh_from_db()
        self.assertEqual(order.status, Order.CANCELLED)

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, initial_stock + 2)

        # Verify inventory history record
        history = InventoryHistory.objects.filter(product=self.product).last()
        self.assertIsNotNone(history)
        self.assertEqual(history.action, InventoryHistory.STOCK_IN)
        self.assertEqual(history.quantity, 2)

    def test_coupon_remove_view(self):
        session = self.client.session
        session["coupon_id"] = 999
        session.save()

        response = self.client.get(reverse("coupons:remove_coupon"))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn("coupon_id", self.client.session)

    def test_download_invoice_generates_valid_pdf(self):
        self.client.login(username="testshopper", password="testpassword123")

        order = Order.objects.create(
            user=self.user,
            full_name="Test Shopper",
            phone="9876543210",
            address="123 Fresh Lane",
            city="Pune",
            state="Maharashtra",
            pincode="411001",
            total_amount=Decimal("120.00"),
            status=Order.CONFIRMED
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=2,
            price=Decimal("60.00")
        )

        response = self.client.get(reverse("orders:download_invoice", args=[order.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertTrue(len(response.content) > 1000)

    def test_live_tracking_auto_creation_and_view(self):
        self.client.login(username="testshopper", password="testpassword123")

        order = Order.objects.create(
            user=self.user,
            full_name="Test Shopper",
            phone="9876543210",
            address="123 Fresh Lane",
            city="Pune",
            state="Maharashtra",
            pincode="411001",
            total_amount=Decimal("120.00"),
            status=Order.CONFIRMED
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=2,
            price=Decimal("60.00")
        )

        tracking = order.get_tracking()
        self.assertIsNotNone(tracking)
        self.assertEqual(tracking.rider_name, "Vikram Shinde")
        self.assertTrue(len(tracking.delivery_pin) >= 4)

        # Test view render
        response = self.client.get(reverse("orders:track", args=[order.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "FreshTrack")
        self.assertContains(response, tracking.rider_name)
        self.assertContains(response, tracking.delivery_pin)

    def test_tracking_api_and_simulation(self):
        self.client.login(username="testshopper", password="testpassword123")

        order = Order.objects.create(
            user=self.user,
            full_name="Test Shopper",
            phone="9876543210",
            address="123 Fresh Lane",
            city="Pune",
            state="Maharashtra",
            pincode="411001",
            total_amount=Decimal("120.00"),
            status=Order.CONFIRMED
        )

        # 1. Test API endpoint
        api_response = self.client.get(reverse("orders:api_track", args=[order.id]))
        self.assertEqual(api_response.status_code, 200)
        data = api_response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["order_id"], order.id)
        self.assertIn("rider_lat", data)
        self.assertIn("rider_lng", data)
        self.assertIn("delivery_pin", data)

        # 2. Test Simulation to ON_THE_WAY
        sim_response = self.client.get(
            reverse("orders:simulate_track", kwargs={"order_id": order.id, "stage": "on_the_way"}),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(sim_response.status_code, 200)
        sim_data = sim_response.json()
        self.assertEqual(sim_data["new_stage"], "ON_THE_WAY")

        # Verify API reflects the simulation
        updated_api = self.client.get(reverse("orders:api_track", args=[order.id])).json()
        self.assertEqual(updated_api["stage"], "ON_THE_WAY")
        self.assertGreater(updated_api["progress"], 50)

        # 3. Test Simulation to DELIVERED
        sim_deliv = self.client.get(
            reverse("orders:simulate_track", kwargs={"order_id": order.id, "stage": "delivered"}),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(sim_deliv.status_code, 200)

        order.refresh_from_db()
        self.assertEqual(order.status, Order.DELIVERED)
        final_api = self.client.get(reverse("orders:api_track", args=[order.id])).json()
        self.assertTrue(final_api["is_delivered"])
        self.assertEqual(final_api["progress"], 100)

    def test_tracking_unauthorized_access_prevented(self):
        other_user = User.objects.create_user(
            username="stranger",
            email="stranger@example.com",
            password="password456"
        )
        self.client.login(username="stranger", password="password456")

        order = Order.objects.create(
            user=self.user,  # belongs to testshopper
            full_name="Test Shopper",
            phone="9876543210",
            address="123 Fresh Lane",
            city="Pune",
            state="Maharashtra",
            pincode="411001",
            total_amount=Decimal("120.00"),
            status=Order.CONFIRMED
        )

        # Accessing another user's tracking view returns 404
        response = self.client.get(reverse("orders:track", args=[order.id]))
        self.assertEqual(response.status_code, 404)

        # Accessing API returns 404
        api_response = self.client.get(reverse("orders:api_track", args=[order.id]))
        self.assertEqual(api_response.status_code, 404)

    def test_update_live_location_api_authenticated(self):
        self.client.login(username="testshopper", password="testpassword123")
        order = Order.objects.create(
            user=self.user,
            full_name="Test Shopper",
            phone="9876543210",
            address="123 Fresh Lane",
            city="Pune",
            state="Maharashtra",
            pincode="411001",
            total_amount=Decimal("120.00"),
            status=Order.CONFIRMED
        )
        url = reverse("orders:update_location", args=[order.id])
        response = self.client.post(
            url,
            data={"lat": 18.5204, "lng": 73.8567, "accuracy": 15},
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["customer_lat"], 18.5204)
        self.assertEqual(data["customer_lng"], 73.8567)
        self.assertGreater(data["distance_km"], 0)

    def test_update_live_location_api_invalid_coords(self):
        self.client.login(username="testshopper", password="testpassword123")
        order = Order.objects.create(
            user=self.user,
            full_name="Test Shopper",
            phone="9876543210",
            address="123 Fresh Lane",
            city="Pune",
            state="Maharashtra",
            pincode="411001",
            total_amount=Decimal("120.00"),
            status=Order.CONFIRMED
        )
        url = reverse("orders:update_location", args=[order.id])
        response = self.client.post(
            url,
            data={"lat": 0, "lng": 0},
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)




