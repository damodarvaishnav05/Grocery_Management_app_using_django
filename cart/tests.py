from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from categories.models import Category
from products.models import Product
from cart.models import Cart
from cart.scanner import parse_line_quantity_and_query, parse_and_match_grocery_list

User = get_user_model()


class SmartScannerAndBatchCartTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="scanner_shopper",
            email="shopper@freshmart.com",
            password="testpassword123"
        )

        self.cat_dairy = Category.objects.create(name="Dairy, Bread & Eggs", slug="dairy", is_active=True)
        self.cat_veg = Category.objects.create(name="Fresh Vegetables", slug="vegetables", is_active=True)

        self.milk = Product.objects.create(
            category=self.cat_dairy,
            name="Fresh Cow Milk - Full Cream (1 Litre)",
            slug="cow-milk-1l",
            price=Decimal("60.00"),
            stock=20,
            available=True
        )

        self.bread = Product.objects.create(
            category=self.cat_dairy,
            name="100% Whole Wheat Bread (400g)",
            slug="whole-wheat-bread",
            price=Decimal("45.00"),
            stock=15,
            available=True
        )

        self.potatoes = Product.objects.create(
            category=self.cat_veg,
            name="Farm Fresh Potatoes (2 kg)",
            slug="potatoes-2kg",
            price=Decimal("50.00"),
            stock=10,
            available=True
        )

    def test_parse_line_quantity_and_query(self):
        # 1. Number + unit + name
        qty, unit, query = parse_line_quantity_and_query("2 litres cow milk")
        self.assertEqual(qty, 2)
        self.assertIn("litre", unit)
        self.assertIn("cow milk", query)

        # 2. Number + packet + name
        qty, unit, query = parse_line_quantity_and_query("1 packet whole wheat bread")
        self.assertEqual(qty, 1)
        self.assertEqual(unit, "packet")
        self.assertIn("whole wheat bread", query)

        # 3. Bullet numbering stripped
        qty, unit, query = parse_line_quantity_and_query("1. 3 kg farm fresh potatoes")
        self.assertEqual(qty, 3)
        self.assertEqual(unit, "kg")
        self.assertIn("potatoes", query)

        # 4. Item without explicit quantity defaults to 1
        qty, unit, query = parse_line_quantity_and_query("- cow milk")
        self.assertEqual(qty, 1)
        self.assertIn("cow milk", query)

    def test_parse_and_match_grocery_list(self):
        text = """
        2 litres cow milk
        1 packet whole wheat bread
        2 kg potatoes
        unknown fantasy fruit xyz
        """
        results = parse_and_match_grocery_list(text)
        self.assertEqual(results["total_items"], 4)
        self.assertEqual(results["matched_count"], 3)
        self.assertEqual(len(results["unmatched"]), 1)

        matched_names = [m["product"].name for m in results["matches"]]
        self.assertIn(self.milk.name, matched_names)
        self.assertIn(self.bread.name, matched_names)
        self.assertIn(self.potatoes.name, matched_names)

        # Check estimated total: (2 * 60) + (1 * 45) + (2 * 50) = 120 + 45 + 100 = 265
        self.assertEqual(results["estimated_total"], Decimal("265.00"))

    def test_smart_scanner_view(self):
        self.client.login(username="scanner_shopper", password="testpassword123")

        # GET request renders template
        response = self.client.get(reverse("cart:smart_scan"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "FreshScan")

        # POST request matches items
        post_response = self.client.post(
            reverse("cart:smart_scan"),
            {"grocery_text": "2 litres cow milk\n1 packet bread"}
        )
        self.assertEqual(post_response.status_code, 200)
        self.assertContains(post_response, "Matched Grocery Basket")
        self.assertContains(post_response, "Fresh Cow Milk")

        # AJAX POST returns JSON
        ajax_response = self.client.post(
            reverse("cart:smart_scan"),
            {"grocery_text": "2 litres cow milk"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(ajax_response.status_code, 200)
        json_data = ajax_response.json()
        self.assertEqual(json_data["status"], "success")
        self.assertEqual(json_data["matched_count"], 1)
        self.assertEqual(json_data["matches"][0]["product_id"], self.milk.id)

    def test_batch_add_to_cart(self):
        self.client.login(username="scanner_shopper", password="testpassword123")

        post_data = {
            "selected_products": [str(self.milk.id), str(self.bread.id)],
            f"quantity_{self.milk.id}": "2",
            f"quantity_{self.bread.id}": "1",
        }

        response = self.client.post(reverse("cart:batch_add"), post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("cart:index"))

        # Verify user cart contains both items
        cart_items = Cart.objects.filter(user=self.user)
        self.assertEqual(cart_items.count(), 2)

        milk_cart = cart_items.get(product=self.milk)
        self.assertEqual(milk_cart.quantity, 2)

        bread_cart = cart_items.get(product=self.bread)
        self.assertEqual(bread_cart.quantity, 1)

