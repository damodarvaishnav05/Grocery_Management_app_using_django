import json
import logging
import os
import re
import urllib.request
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse

from products.models import Product
from categories.models import Category
from cart.models import Cart
from cart.scanner import find_best_product_match

logger = logging.getLogger(__name__)

# Built-in recipe knowledge base for instant 1-click recipe ordering
RECIPES_DATABASE = {
    "paneer butter masala": {
        "dish_name": "Restaurant-Style Paneer Butter Masala",
        "prep_time": "20 Mins",
        "servings": "3 - 4 Servings",
        "cuisine": "North Indian",
        "summary": "Rich, creamy cottage cheese curry simmered in a velvety spiced tomato, butter, and cashew gravy.",
        "steps": [
            "Melt 2 tbsp Amul butter in a pan, sauté finely chopped onions until translucent and golden.",
            "Add ginger-garlic paste and pureed tomatoes. Simmer on medium flame until butter separates.",
            "Stir in garam masala, kasoori methi, and fresh cream for that luxurious restaurant texture.",
            "Gently fold in fresh Paneer cubes, simmer for 3 minutes, and serve hot with rotis or rice."
        ],
        "ingredients": ["paneer", "amul butter", "tomato", "onion", "ginger", "milk", "fortune sunflower oil"]
    },
    "masala chai": {
        "dish_name": "Kadak Adrak Masala Chai & Evening Nashta",
        "prep_time": "8 Mins",
        "servings": "2 - 3 Cups",
        "cuisine": "Everyday Indian",
        "summary": "Invigorating spiced milk tea infused with crushed fresh ginger, served alongside tea-time snacks.",
        "steps": [
            "Bring 1.5 cups water to a rolling boil with crushed fresh ginger and cardamom.",
            "Add 2 teaspoons Tata Tea Gold leaves, simmer for 2 minutes until deep amber color develops.",
            "Pour in 1 cup fresh Amul milk, bring to a boil twice, strain into cups, and enjoy with Parle-G or biscuits."
        ],
        "ingredients": ["tata tea gold", "amul taaza milk", "ginger", "sugar", "kurkure masala", "lays magic masala"]
    },
    "maggi noodles feast": {
        "dish_name": "Street-Style Cheesy Butter Maggi",
        "prep_time": "7 Mins",
        "servings": "1 - 2 Servings",
        "cuisine": "Quick Snack",
        "summary": "Indulgent 2-minute instant noodles tossed with sautéed fresh veggies, melting butter, and secret spices.",
        "steps": [
            "In a hot pan, melt 1 tbsp Amul butter and lightly sauté diced tomatoes and green chillies.",
            "Pour in 1.5 cups of boiling water and mix in the Maggi Tastemaker thoroughly.",
            "Break in the Maggi noodle cake, cook for 2 minutes on high flame, and serve steaming hot."
        ],
        "ingredients": ["maggi noodles", "amul butter", "tomato", "onion", "maaza mango drink"]
    },
    "dal tadka": {
        "dish_name": "Dhaba-Style Yellow Dal Tadka & Jeera Rice",
        "prep_time": "22 Mins",
        "servings": "4 Servings",
        "cuisine": "Homestyle Indian",
        "summary": "Comforting yellow lentils tempered with crackling cumin seeds, garlic, onions, and golden ghee/oil.",
        "steps": [
            "Pressure cook washed dal with turmeric, salt, and water for 3 to 4 whistles until soft.",
            "In a small pan, heat cooking oil, crackle cumin seeds, sliced garlic cloves, and chopped onions.",
            "Toss in diced juicy tomatoes and red chilli powder. Fry until aromatic.",
            "Pour the sizzling tadka over the cooked dal, stir well, and garnish with fresh coriander."
        ],
        "ingredients": ["fortune sunflower oil", "tomato", "onion", "ginger", "aashirvaad atta"]
    },
    "fruit salad bowl": {
        "dish_name": "Vitamin Booster Fresh Fruit Bowl",
        "prep_time": "5 Mins",
        "servings": "2 Servings",
        "cuisine": "Healthy & Clean",
        "summary": "Hand-picked farm apples, bananas, sweet oranges, and seasonal fruits drizzled with honey and lime.",
        "steps": [
            "Wash and dice fresh apples, peel and slice sweet bananas into a clean bowl.",
            "Separate sweet orange segments and toss gently together.",
            "Drizzle with raw honey or a pinch of chaat masala for a refreshing antioxidant punch."
        ],
        "ingredients": ["apple", "banana", "orange", "maaza mango drink"]
    },
    "quick breakfast combo": {
        "dish_name": "10-Minute Power Breakfast (Oats & Coffee)",
        "prep_time": "6 Mins",
        "servings": "1 - 2 Servings",
        "cuisine": "Breakfast Essentials",
        "summary": "Quick nourishing rolled oats in warm milk paired with aromatic Nescafe Classic coffee.",
        "steps": [
            "Simmer rolled oats in 1 cup warm Amul milk for 3 minutes until thick and creamy.",
            "Froth 1 tsp Nescafe Classic with hot milk and brown sugar for a barista-style morning coffee.",
            "Top your oats bowl with sliced bananas or apple chunks."
        ],
        "ingredients": ["nescafe classic", "amul taaza milk", "amul butter", "apple"]
    }
}


def match_recipe_from_query(query):
    """Detects if query matches any known recipes or cooking keywords"""
    q = query.lower().strip()

    # Direct match or alias check
    if any(k in q for k in ["paneer", "butter masala", "shahi paneer", "kadai paneer"]):
        return RECIPES_DATABASE["paneer butter masala"]
    elif any(k in q for k in ["tea", "chai", "evening nashta", "adrak chai", "tea time"]):
        return RECIPES_DATABASE["masala chai"]
    elif any(k in q for k in ["maggi", "noodles", "instant noodle", "magi"]):
        return RECIPES_DATABASE["maggi noodles feast"]
    elif any(k in q for k in ["dal", "tadka", "dal fry", "dal chawal", "lentil"]):
        return RECIPES_DATABASE["dal tadka"]
    elif any(k in q for k in ["fruit bowl", "fruit salad", "fruits", "fruit"]):
        return RECIPES_DATABASE["fruit salad bowl"]
    elif any(k in q for k in ["coffee", "oats", "morning breakfast", "breakfast combo"]):
        return RECIPES_DATABASE["quick breakfast combo"]

    # If user explicitly asks "recipe for ...", "how to cook ...", "make ..."
    if any(q.startswith(prefix) for prefix in ["recipe for", "how to make", "how to cook", "make", "cook"]):
        # Fallback to paneer butter masala or first available recipe as smart demonstration
        return RECIPES_DATABASE["paneer butter masala"]

    return None


def get_ai_response(question):
    q = question.lower().strip()

    if any(k in q for k in ["weight loss", "lose weight", "diet food", "burn fat", "low calorie"]):
        return {
            "title": "🥗 Weight Loss & Calorie-Smart Grocery Guide",
            "category": "Diet & Fitness",
            "summary": "Focus on high-volume, low-calorie foods with ample fiber and lean protein to keep you satiated while maintaining a calorie deficit.",
            "points": [
                ("High-Fiber Vegetables", "Broccoli, spinach, cauliflower, cucumbers, bell peppers, zucchini (fill half your plate)."),
                ("Low-Glycemic Fruits", "Crisp apples, strawberries, blueberries, papaya, oranges, and grapefruit."),
                ("Lean Proteins", "Paneer, tofu, boiled eggs, Greek yogurt, chickpeas, and yellow moong dal."),
                ("Complex Carbohydrates", "Rolled oats, quinoa, brown rice, millets (ragi/jowar), and sweet potatoes."),
                ("Metabolism Boosters", "Green tea, lemon water, chia seeds, apple cider vinegar, and cinnamon.")
            ],
            "avoid": ["Sugary beverages & sodas", "Ultra-processed fried snacks", "Refined white flour (maida)", "Excess cooking oils"],
            "suggested_query": "apple"
        }
    elif any(k in q for k in ["protein", "muscle", "gym", "bodybuilding", "workout food"]):
        return {
            "title": "💪 High-Protein Nutrition Powerhouses",
            "category": "Fitness & Nutrition",
            "summary": "Essential grocery picks to hit your daily protein targets (aim for 1.2g - 2.0g per kg of body weight for active individuals).",
            "points": [
                ("Dairy & Alternatives", "Cottage cheese (Paneer), fresh cow milk, Greek yogurt, soya chunks (52% protein), tofu."),
                ("Eggs & Whole Proteins", "Farm fresh eggs (6g protein/egg) — great for breakfast or post-workout meals."),
                ("Legumes & Pulses", "Chickpeas (chana), rajma, green gram (moong sprouts), black lentils, and edamame."),
                ("Nuts & Seeds", "Peanut butter (no added sugar), almonds, walnuts, pumpkin seeds, hemp hearts."),
                ("Grains", "Quinoa, protein oats, and amaranth.")
            ],
            "tip": "Distribute protein evenly across 3 to 4 meals every day for optimal muscle protein synthesis.",
            "suggested_query": "milk"
        }
    elif any(k in q for k in ["diabetes", "blood sugar", "diabetic", "glycemic"]):
        return {
            "title": "🩺 Diabetes-Friendly & Low-GI Grocery Picks",
            "category": "Health & Wellness",
            "summary": "Choose foods with a low Glycemic Index (GI < 55) that release glucose steadily into the bloodstream.",
            "points": [
                ("Low GI Grains", "Steel-cut oats, barley, quinoa, whole wheat, and ragi."),
                ("Non-Starchy Vegetables", "Bitter gourd (karela), methi (fenugreek leaves), spinach, okra (bhindi), cucumber, and cauliflower."),
                ("Smart Fruits", "Guava, berries, amla (Indian gooseberry), jamun, and green apples."),
                ("Healthy Fats", "Extra virgin olive oil, cold-pressed mustard oil, soaked almonds, and flaxseeds."),
                ("Herbal Allies", "Fenugreek seeds, cinnamon stick tea, and ginger.")
            ],
            "avoid": ["Fruit juices & carbonated soft drinks", "White bread, white rice & refined pasta", "Packaged sweets & syrups"],
            "suggested_query": "vegetable"
        }
    elif any(k in q for k in ["heart", "cholesterol", "blood pressure", "cardio", "bp"]):
        return {
            "title": "❤️ Heart Health & Cholesterol Management",
            "category": "Cardio Wellness",
            "summary": "Support cardiovascular vitality with foods rich in soluble fiber, Omega-3 fatty acids, and potassium.",
            "points": [
                ("Soluble Fiber Champions", "Oats, barley, beans, and lentils help bind cholesterol in the digestive tract."),
                ("Omega-3 & Healthy Fats", "Flaxseed oil, walnuts, chia seeds, and sunflower oil."),
                ("Potassium-Rich Produce", "Bananas, sweet potatoes, tomatoes, and tender coconut water."),
                ("Antioxidant Boosters", "Pomegranates, dark berries, garlic cloves, and beetroot.")
            ],
            "tip": "Cut down on sodium intake and avoid trans-fats found in commercial fried foods and hydrogenated oils.",
            "suggested_query": "oil"
        }
    elif any(k in q for k in ["delivery", "order", "shipping", "track", "how long", "time"]):
        return {
            "title": "🚚 Express Delivery & Order Information",
            "category": "Store Support",
            "summary": "Everything you need to know about Om Super Mart deliveries and tracking:",
            "points": [
                ("Ultra-Fast 10-Min Delivery", "Fresh produce and essentials delivered to your doorstep in 10 to 15 minutes across covered zones."),
                ("Real-time Status Tracking", "Track your order status live with interactive GPS map in the 'My Orders' tab."),
                ("Free Delivery Threshold", "Enjoy 100% Free Express Delivery on orders above ₹199."),
                ("Secure 4-Digit Delivery PIN", "Share your delivery PIN with our partner to safely receive your groceries.")
            ],
            "suggested_query": "milk"
        }
    elif any(k in q for k in ["coupon", "discount", "offer", "promo", "code"]):
        from datetime import date
        today_code = f"OMSUPER{date.today().strftime('%d%m')}"
        return {
            "title": "🎉 Coupons, Offers & Today's Special Code",
            "category": "Promotions",
            "summary": "Maximize your grocery savings every day on Om Super Mart:",
            "points": [
                (f"Today's Active Coupon: {today_code}", f"Apply code '{today_code}' at checkout to unlock an instant 10% discount on your order!"),
                ("First Order Bonus", "New customers get free delivery automatically credited to their account."),
                ("Combos & Bundles", "Explore weekly vegetable combos and breakfast bundles in the Products catalog.")
            ],
            "suggested_query": "fortune"
        }
    else:
        return {
            "title": "🤖 Welcome to Om Super Mart AI Grocery Assistant",
            "category": "General Guide",
            "summary": f"You asked: \"{question}\". I am trained to give you immediate expert guidance on recipes, grocery checklists, nutrition, and store assistance.",
            "points": [
                ("1-Click Recipe-to-Cart", "Ask for 'Paneer Butter Masala', 'Masala Chai', 'Dal Tadka', or 'Cheesy Maggi' to get ingredients added directly to your cart."),
                ("Health & Dietary Plans", "Ask for 'foods for weight loss', 'protein rich diet', or 'diabetes friendly groceries'."),
                ("Produce & Freshness", "Ask for 'fresh fruits recommendations' or 'how to store veggies'."),
                ("Store Assistance", "Ask about 'delivery time', 'active coupons', or 'payment options'.")
            ],
            "tip": "Try searching for a recipe below (e.g. 'Paneer Butter Masala') to see 1-click cart addition in action!",
            "suggested_query": "paneer"
        }


def index(request):
    answer = None
    recipe_data = None
    user_query = ""
    matching_products = []

    if request.method == "POST":
        user_query = request.POST.get("question", "").strip()
        if user_query:
            # Check for recipe match first
            matched_recipe = match_recipe_from_query(user_query)
            if matched_recipe:
                catalog_products = list(Product.objects.filter(available=True).select_related("category"))
                matched_items = []
                total_recipe_price = Decimal("0.00")

                for ing in matched_recipe["ingredients"]:
                    best_prod, score = find_best_product_match(ing, catalog_products)
                    if best_prod:
                        matched_items.append({
                            "ingredient_name": ing.title(),
                            "product": best_prod,
                            "price": best_prod.final_price,
                            "in_stock": best_prod.stock > 0,
                            "score": score,
                        })
                        total_recipe_price += Decimal(str(best_prod.final_price))
                    else:
                        matched_items.append({
                            "ingredient_name": ing.title(),
                            "product": None,
                            "price": Decimal("0.00"),
                            "in_stock": False,
                            "score": 0,
                        })

                recipe_data = {
                    "dish_name": matched_recipe["dish_name"],
                    "prep_time": matched_recipe["prep_time"],
                    "servings": matched_recipe["servings"],
                    "cuisine": matched_recipe["cuisine"],
                    "summary": matched_recipe["summary"],
                    "steps": matched_recipe["steps"],
                    "items": matched_items,
                    "total_price": total_recipe_price,
                    "available_items_count": sum(1 for i in matched_items if i["product"] and i["in_stock"]),
                    "total_items_count": len(matched_items),
                }

            # Also provide the AI contextual guidance
            answer = get_ai_response(user_query)

            # Look up related products for the catalog carousel
            suggested_term = answer.get("suggested_query")
            if suggested_term:
                matching_products = Product.objects.filter(
                    available=True,
                    name__icontains=suggested_term
                )[:4]
            if not matching_products:
                matching_products = Product.objects.filter(available=True)[:4]

    categories = Category.objects.filter(is_active=True)[:8]

    return render(
        request,
        "ai_assistant/index.html",
        {
            "answer": answer,
            "recipe_data": recipe_data,
            "user_query": user_query,
            "matching_products": matching_products,
            "categories": categories,
        }
    )


@login_required
def add_recipe_to_cart(request):
    """
    1-Click bulk recipe addition.
    Takes a list of product IDs matched for a recipe and adds them into the customer's cart.
    """
    if request.method == "POST":
        product_ids = request.POST.getlist("product_ids")
        dish_name = request.POST.get("dish_name", "Recipe")
        added_count = 0

        for pid in product_ids:
            try:
                prod = Product.objects.get(id=int(pid), available=True)
                if prod.stock > 0:
                    cart_item, created = Cart.objects.get_or_create(user=request.user, product=prod)
                    if not created:
                        if cart_item.quantity < prod.stock:
                            cart_item.quantity += 1
                            cart_item.save()
                    added_count += 1
            except (Product.DoesNotExist, ValueError):
                continue

        if added_count > 0:
            messages.success(
                request,
                f"⚡ Added {added_count} fresh ingredients for '{dish_name}' to your cart! Ready for 10-minute delivery."
            )
            return redirect("cart:index")
        else:
            messages.warning(request, "Selected ingredients are currently out of stock.")
            return redirect("ai_assistant:index")

    return redirect("ai_assistant:index")
