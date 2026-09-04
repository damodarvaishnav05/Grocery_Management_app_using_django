from django.test import TestCase, Client
from django.urls import reverse


class AIAssistantTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_ai_page_get(self):
        response = self.client.get(reverse("ai_assistant:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "FreshMart AI Shopping & Nutrition Guide")
        self.assertContains(response, "Weight Loss Foods")

    def test_ai_query_weight_loss(self):
        response = self.client.post(
            reverse("ai_assistant:index"),
            {"question": "Suggest some foods for weight loss"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Weight Loss")
        self.assertContains(response, "Calorie-Smart Grocery Guide")

    def test_ai_query_protein(self):
        response = self.client.post(
            reverse("ai_assistant:index"),
            {"question": "What are high protein groceries for gym?"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "High-Protein Nutrition Powerhouses")

    def test_ai_query_storage(self):
        response = self.client.post(
            reverse("ai_assistant:index"),
            {"question": "How to keep vegetables fresh?"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Keep Produce Fresh 2x Longer")
