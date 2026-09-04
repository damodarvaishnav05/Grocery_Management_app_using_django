from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from categories.models import Category
from products.models import Product
from cart.models import Cart

User = get_user_model()


class GroceryProductTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(
            name="Organic Fruits",
            slug="organic-fruits",
            is_active=True
        )
        self.product = Product.objects.create(
            category=self.category,
            name="Honey Crisp Apple",
            slug="honey-crisp-apple",
            description="Sweet crisp apple",
            price=Decimal("120.00"),
            discount_price=Decimal("99.00"),
            stock=20,
            available=True
        )

    def test_final_price_uses_discount_price(self):
        self.assertEqual(self.product.final_price, Decimal("99.00"))

    def test_final_price_without_discount(self):
        self.product.discount_price = None
        self.product.save()
        self.assertEqual(self.product.final_price, Decimal("120.00"))

    def test_home_page_loads_and_displays_product(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Honey Crisp Apple")

    def test_catalog_search_filters_correctly(self):
        response = self.client.get(reverse("products:index") + "?q=Crisp")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Honey Crisp Apple")

    def test_product_detail_page(self):
        response = self.client.get(reverse("products:detail", args=[self.product.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Honey Crisp Apple")
        self.assertContains(response, "99.00")

    def test_voice_command_empty_returns_400(self):
        url = reverse("products:voice_command_api")
        response = self.client.post(url, data={"command": ""}, content_type="application/json")
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["status"], "error")

    def test_voice_command_navigation_cart(self):
        url = reverse("products:voice_command_api")
        response = self.client.post(url, data={"command": "open my cart"}, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["action"], "navigate")
        self.assertEqual(data["url"], "/cart/")

    def test_voice_command_navigation_wallet(self):
        url = reverse("products:voice_command_api")
        response = self.client.get(url + "?command=show my wallet balance")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["action"], "navigate")
        self.assertEqual(data["url"], "/wallet/")

    def test_voice_command_search_intent(self):
        url = reverse("products:voice_command_api")
        response = self.client.post(url, data={"command": "find Honey Crisp Apple"}, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["action"], "search")
        self.assertIn("honey crisp apple", data["query"].lower())
        self.assertGreaterEqual(data["count"], 1)

    def test_voice_command_add_to_cart_authenticated(self):
        user = User.objects.create_user(email="voice@freshmart.com", username="voicetester", password="password123")
        self.client.login(username="voicetester", password="password123")
        url = reverse("products:voice_command_api")
        response = self.client.post(url, data={"command": "add 2 Honey Crisp Apple"}, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["action"], "added_to_cart")
        self.assertEqual(data["quantity"], 2)

    def test_voice_command_add_to_cart_unauthenticated(self):
        url = reverse("products:voice_command_api")
        response = self.client.post(url, data={"command": "add 1 Honey Crisp Apple"}, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["action"], "navigate")
        self.assertIn(self.product.slug, data["url"])

    def test_product_auto_generates_barcode_on_save(self):
        self.assertIsNotNone(self.product.barcode)
        self.assertTrue(self.product.barcode.startswith("890103"))

    def test_barcode_lookup_api_valid_code(self):
        url = reverse("products:barcode_lookup_api")
        response = self.client.get(f"{url}?barcode={self.product.barcode}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["product"]["name"], "Honey Crisp Apple")
        self.assertEqual(data["product"]["barcode"], self.product.barcode)
        self.assertEqual(data["product"]["final_price"], 99.0)

    def test_barcode_lookup_api_not_found(self):
        url = reverse("products:barcode_lookup_api")
        response = self.client.get(f"{url}?barcode=9999999999999")
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data["status"], "not_found")

    def test_barcode_lookup_api_missing_barcode(self):
        url = reverse("products:barcode_lookup_api")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)

    def test_barcode_add_to_cart_authenticated(self):
        user = User.objects.create_user(email="barcodetester@freshmart.com", username="barcodetester", password="password123")
        self.client.login(username="barcodetester", password="password123")

        url = reverse("products:barcode_add_to_cart_api")
        response = self.client.post(
            url,
            data={"barcode": self.product.barcode, "quantity": 3},
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["quantity"], 3)

        cart_item = Cart.objects.get(user=user, product=self.product)
        self.assertEqual(cart_item.quantity, 3)

    def test_barcode_add_to_cart_unauthenticated(self):
        url = reverse("products:barcode_add_to_cart_api")
        response = self.client.post(
            url,
            data={"barcode": self.product.barcode, "quantity": 1},
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertEqual(data["status"], "auth_required")

    def test_barcode_add_to_cart_out_of_stock(self):
        user = User.objects.create_user(email="stocktester@freshmart.com", username="stocktester", password="password123")
        self.client.login(username="stocktester", password="password123")

        self.product.stock = 0
        self.product.save()

        url = reverse("products:barcode_add_to_cart_api")
        response = self.client.post(
            url,
            data={"barcode": self.product.barcode, "quantity": 1},
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["status"], "out_of_stock")

    def test_barcode_scanner_view_renders(self):
        url = reverse("products:barcode_scanner")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "products/barcode_scanner.html")
        self.assertContains(response, "FreshBarcode")


