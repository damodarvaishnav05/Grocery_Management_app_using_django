from django.shortcuts import render


def index(request):

    answer = ""

    if request.method == "POST":

        question = request.POST.get(
            "question",
            ""
        ).lower()

        # ==========================
        # APP FEATURES
        # ==========================

        if (
            "feature" in question
            or "app" in question
            or "freshmart" in question
        ):

            answer = """
🛒 FreshMart Features

✅ User Registration & Login

✅ Product Categories

✅ Product Search

✅ Product Details Page

✅ Shopping Cart

✅ Wishlist

✅ Checkout System

✅ Order Management

✅ Coupons & Discounts

✅ Product Reviews & Ratings

✅ User Profile Management

✅ AI Shopping Assistant

✅ Inventory Management

✅ Admin Dashboard

✅ Responsive Design

FreshMart helps customers browse products,
manage carts, place orders, save wishlists,
apply coupons and get grocery suggestions.
"""

        # ==========================
        # WEIGHT LOSS
        # ==========================

        elif "weight loss" in question:

            answer = """
🥗 Recommended Weight Loss Foods

• Oats
• Apples
• Green Tea
• Almonds
• Brown Bread
• Cucumber

Tip:
Avoid sugary drinks and junk food.
"""

        # ==========================
        # PROTEIN
        # ==========================

        elif "protein" in question:

            answer = """
💪 Protein Rich Foods

• Eggs
• Paneer
• Milk
• Peanut Butter
• Yogurt
• Chickpeas

These foods help build muscles and keep you full longer.
"""

        # ==========================
        # BREAKFAST
        # ==========================

        elif "breakfast" in question:

            answer = """
🍳 Healthy Breakfast Ideas

• Oats + Banana
• Milk + Dry Fruits
• Peanut Butter Toast
• Vegetable Sandwich
• Poha
• Upma
"""

        # ==========================
        # FRUITS
        # ==========================

        elif "fruit" in question:

            answer = """
🍎 Recommended Fruits

• Apple
• Banana
• Orange
• Papaya
• Watermelon
• Grapes

Rich in vitamins and fiber.
"""

        # ==========================
        # VEGETABLES
        # ==========================

        elif "vegetable" in question:

            answer = """
🥦 Healthy Vegetables

• Broccoli
• Spinach
• Carrot
• Tomato
• Cabbage
• Cucumber
"""

        # ==========================
        # DIABETES
        # ==========================

        elif "diabetes" in question:

            answer = """
🩺 Foods For Diabetes

• Oats
• Brown Rice
• Green Vegetables
• Nuts
• Lentils

Avoid:

❌ Soft Drinks
❌ White Sugar
❌ Sweets
"""

        # ==========================
        # DIET PLAN
        # ==========================

        elif "diet" in question:

            answer = """
📋 Simple Daily Diet Plan

Breakfast:
• Oats + Milk

Lunch:
• Rice + Dal + Salad

Evening:
• Fruits

Dinner:
• Chapati + Vegetables

Drink plenty of water.
"""

        # ==========================
        # CART
        # ==========================

        elif "cart" in question:

            answer = """
🛒 Shopping Cart

• Add products to your cart
• Increase or decrease quantity
• Remove unwanted products
• Apply coupons
• Proceed to checkout
"""

        # ==========================
        # WISHLIST
        # ==========================

        elif "wishlist" in question:

            answer = """
❤️ Wishlist

Save products for later purchase.

Features:

• Add products to wishlist
• Remove products anytime
• Quickly move items to cart
"""

        # ==========================
        # COUPONS
        # ==========================

        elif "coupon" in question:

            answer = """
🎉 Coupons & Discounts

Use available coupon codes during checkout.

Benefits:

• Instant discounts
• Special offers
• Seasonal deals
"""

        # ==========================
        # DELIVERY
        # ==========================

        elif "delivery" in question:

            answer = """
🚚 Delivery Information

• Fast delivery
• Secure packaging
• Real-time order updates
• Fresh products guaranteed
"""

        # ==========================
        # PAYMENT
        # ==========================

        elif "payment" in question:

            answer = """
💳 Payment Options

• Cash On Delivery

Future Support:

• Razorpay
• UPI
• Debit Card
• Credit Card
• Net Banking
"""

        # ==========================
        # PRODUCTS
        # ==========================

        elif "product" in question:

            answer = """
📦 FreshMart Products

Available Categories:

• Fruits
• Vegetables
• Dairy
• Bakery
• Beverages
• Snacks
• Personal Care

Browse products from the Products page.
"""

        # ==========================
        # DEFAULT
        # ==========================

        else:

            answer = """
🤖 Welcome to FreshMart AI Assistant

I can help with:

• App Features
• Products
• Shopping Cart
• Wishlist
• Coupons
• Delivery
• Payments
• Weight Loss Foods
• Protein Rich Foods
• Healthy Breakfast
• Fruits
• Vegetables
• Diet Plans
• Diabetes Friendly Foods

Try asking:

• What features does this app have?
• Tell me about cart
• How does wishlist work?
• Suggest foods for weight loss
• Give me a healthy breakfast plan
"""

    return render(
        request,
        "ai_assistant/index.html",
        {
            "answer": answer
        }
    )