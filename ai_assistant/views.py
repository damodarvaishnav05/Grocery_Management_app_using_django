from django.shortcuts import render
from products.models import Product
from categories.models import Category


def get_ai_response(question):
    q = question.lower().strip()

    # ==========================================
    # 1. WEIGHT LOSS & CALORIE MANAGEMENT
    # ==========================================
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

    # ==========================================
    # 2. HIGH PROTEIN & MUSCLE BUILDING
    # ==========================================
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

    # ==========================================
    # 3. DIABETES & BLOOD SUGAR CARE
    # ==========================================
    elif any(k in q for k in ["diabetes", "blood sugar", "diabetic", "glycemic"]):
        return {
            "title": "🩺 Diabetes-Friendly & Low-GI Grocery Picks",
            "category": "Health & Wellness",
            "summary": "Choose foods with a low Glycemic Index (GI < 55) that release glucose steadily into the bloodstream.",
            "points": [
                ("Low GI Grains", "Steel-cut oats, barley, quinoa, whole wheat, and ragi."),
                ("Non-Starchy Vegetables", "Bitter gourd (karela), methi (fenugreek leaves), spinach, okra (bhindi), cucumber, and cauliflower."),
                ("Smart Fruits (Portion Controlled)", "Guava, berries, amla (Indian gooseberry), jamun, and green apples."),
                ("Healthy Fats", "Extra virgin olive oil, cold-pressed mustard oil, soaked almonds, and flaxseeds."),
                ("Herbal Allies", "Fenugreek seeds, cinnamon stick tea, and ginger.")
            ],
            "avoid": ["Fruit juices & carbonated soft drinks", "White bread, white rice & refined pasta", "Packaged sweets & honey syrups"],
            "suggested_query": "vegetable"
        }

    # ==========================================
    # 4. HEART HEALTH & CHOLESTEROL
    # ==========================================
    elif any(k in q for k in ["heart", "cholesterol", "blood pressure", "cardio", "bp"]):
        return {
            "title": "❤️ Heart Health & Cholesterol Management",
            "category": "Cardio Wellness",
            "summary": "Support cardiovascular vitality with foods rich in soluble fiber, Omega-3 fatty acids, and potassium.",
            "points": [
                ("Soluble Fiber Champions", "Oats, barley, beans, and lentils help bind cholesterol in the digestive tract."),
                ("Omega-3 & Healthy Fats", "Flaxseed oil, walnuts, chia seeds, and avocado."),
                ("Potassium-Rich Produce", "Bananas, sweet potatoes, tomatoes, and tender coconut water (helps balance sodium)."),
                ("Antioxidant Boosters", "Pomegranates, dark berries, garlic cloves, and beetroot.")
            ],
            "tip": "Cut down on sodium intake and avoid trans-fats found in commercial fried foods and hydrogenated oils.",
            "suggested_query": "oats"
        }

    # ==========================================
    # 5. IMMUNITY BOOSTING
    # ==========================================
    elif any(k in q for k in ["immunity", "immune", "cold", "flu", "vitamin c", "antioxidant"]):
        return {
            "title": "🛡️ Immunity Boosting Superfoods",
            "category": "Vitality & Wellness",
            "summary": "Fortify your body's immune defense with vitamins C, D, A, Zinc, and natural antimicrobials.",
            "points": [
                ("Vitamin C Stars", "Amla, oranges, lemons, kiwis, guavas, and bell peppers."),
                ("Spices & Roots", "Fresh ginger, raw turmeric, garlic, black pepper, and cloves."),
                ("Herbal Infusions", "Tulsi leaves, green tea, and warm water with honey."),
                ("Gut Health", "Probiotic curd, yogurt, and fermented foods (70% of immunity resides in your gut!)."),
                ("Zinc & Selenium", "Pumpkin seeds, almonds, and sunflower seeds.")
            ],
            "suggested_query": "orange"
        }

    # ==========================================
    # 6. QUICK BREAKFAST IDEAS
    # ==========================================
    elif any(k in q for k in ["breakfast", "morning", "fast meal", "quick food"]):
        return {
            "title": "🍳 Quick & Energizing Healthy Breakfast Ideas",
            "category": "Recipes & Meal Prep",
            "summary": "5 to 10 minute wholesome breakfast recipes made with FreshMart groceries:",
            "points": [
                ("Power Oatmeal Bowl", "Cook rolled oats in warm milk or almond milk, top with sliced banana, chia seeds, and a drizzle of honey."),
                ("Avocado & Boiled Egg Toast", "Whole grain bread toasted with mashed avocado, lime juice, chili flakes, and sliced boiled eggs."),
                ("Protein Smoothie", "Blend 1 banana, a spoonful of peanut butter, 1 glass milk, and a handful of spinach (you won't taste the greens!)."),
                ("Vegetable Poha or Upma", "Flattened rice sautéed with mustard seeds, curry leaves, crunchy peanuts, peas, and carrots."),
                ("Paneer Bhurji with Multigrain Roti", "Scrambled cottage cheese tossed with diced tomatoes, onions, coriander, and light spices.")
            ],
            "suggested_query": "bread"
        }

    # ==========================================
    # 7. GROCERY STORAGE & FRESHNESS TIPS
    # ==========================================
    elif any(k in q for k in ["store", "fresh", "preserve", "spoil", "shelf life", "keep fresh"]):
        return {
            "title": "🌿 Kitchen Secret: Keep Produce Fresh 2x Longer",
            "category": "Smart Kitchen Tips",
            "summary": "Simple, scientifically proven storage techniques to prevent food waste and keep groceries fresh:",
            "points": [
                ("Leafy Greens (Spinach, Coriander)", "Wash, thoroughly dry in a salad spinner or towel, wrap in paper towels, and store in an airtight container in the crisper drawer."),
                ("Tomatoes & Bananas", "Keep at room temperature! Refrigerator cold breaks down tomato cell walls making them mealy."),
                ("Apples & Citrus", "Store in the fridge crisper away from greens (apples emit ethylene gas which accelerates ripening of other produce)."),
                ("Potatoes & Onions", "Store in a cool, dark, ventilated basket. Never store potatoes and onions together as they cause each other to sprout."),
                ("Bread", "Keep at room temperature in a bread box or paper bag; freeze sliced loaves for long term; never refrigerate (refrigeration stales bread faster)."),
                ("Herbs (Mint, Basil)", "Trim stems and place upright in a small glass with 1 inch of water like a bouquet.")
            ],
            "suggested_query": "vegetables"
        }

    # ==========================================
    # 8. SHOPPING CART, DELIVERY & ORDERS
    # ==========================================
    elif any(k in q for k in ["delivery", "order", "shipping", "track", "cancel", "how long", "time"]):
        return {
            "title": "🚚 Express Delivery & Order Information",
            "category": "Store Support",
            "summary": "Everything you need to know about FreshMart deliveries and tracking:",
            "points": [
                ("Ultra-Fast 10-Min Delivery", "Fresh produce and essentials delivered to your doorstep in 10 to 15 minutes across covered zones."),
                ("Real-time Status Tracking", "Track your order status live (Pending -> Confirmed -> Shipped -> Delivered) in the 'My Orders' tab."),
                ("Free Delivery Threshold", "Enjoy 100% Free Express Delivery on orders above ₹199."),
                ("Hassle-Free Cancellation", "Cancel pending or confirmed orders instantly from 'My Orders' before dispatch with immediate inventory and refund processing."),
                ("PDF Invoices", "Download official GST/itemized invoices for all past orders with one click.")
            ],
            "suggested_query": "apple"
        }

    # ==========================================
    # 9. COUPONS & DISCOUNTS
    # ==========================================
    elif any(k in q for k in ["coupon", "discount", "offer", "promo", "voucher", "save money", "code"]):
        from datetime import date
        today_code = f"FRESH{date.today().strftime('%d%m')}"
        return {
            "title": "🎉 Coupons, Offers & Today's Special Code",
            "category": "Promotions",
            "summary": "Maximize your grocery savings every day on FreshMart:",
            "points": [
                (f"Today's Active Coupon: {today_code}", f"Apply code '{today_code}' at checkout to unlock an instant 10% discount on your order!"),
                ("First Order Bonus", "New customers get free delivery and welcome vouchers automatically credited to their account."),
                ("Combos & Bundles", "Explore weekly vegetable combos and breakfast bundles in the Products catalog for up to 25% savings."),
                ("Easy Removal & Reapply", "You can easily apply or remove coupon codes on the Shopping Cart page.")
            ],
            "suggested_query": "fruits"
        }

    # ==========================================
    # 10. PAYMENTS & RAZORPAY
    # ==========================================
    elif any(k in q for k in ["payment", "pay", "razorpay", "upi", "card", "cod", "cash"]):
        return {
            "title": "💳 Payment Options & Security",
            "category": "Checkout Support",
            "summary": "Multiple convenient and bank-grade secure payment methods:",
            "points": [
                ("UPI", "Instant payments with Google Pay, PhonePe, Paytm, and BHIM."),
                ("Credit & Debit Cards", "Visa, MasterCard, RuPay, and American Express with 3D-Secure 2FA."),
                ("Net Banking", "Direct payment supported across all major banks."),
                ("Cash on Delivery (COD)", "Pay with cash or scan QR code upon doorstep delivery."),
                ("SSL Encrypted", "All transactions are 256-bit encrypted via Razorpay certified gateway.")
            ],
            "suggested_query": "milk"
        }

    # ==========================================
    # 11. FRUITS & VEGETABLES
    # ==========================================
    elif any(k in q for k in ["fruit", "vegetable", "veggie", "organic", "greens", "produce"]):
        return {
            "title": "🍎 Farm-Fresh Fruits & Vegetables Guide",
            "category": "Product Discovery",
            "summary": "Hand-picked from certified local farms daily with zero artificial ripening agents:",
            "points": [
                ("Fresh Fruits", "Apples, Cavendish Bananas, Alphonso Mangoes, Pomegranates, Papayas, Sweet Oranges, and Strawberries."),
                ("Daily Cooking Veggies", "Farm Potatoes, Red Onions, Juicy Tomatoes, Fresh Ginger, and Green Chillies."),
                ("Nutritious Greens", "Baby Spinach (Palak), Coriander, Mint, and Methi leaves harvested every morning."),
                ("Crunchy Salad Staples", "English Cucumbers, Hybrid Carrots, Iceberg Lettuce, and Bell Peppers.")
            ],
            "suggested_query": "apple"
        }

    # ==========================================
    # 12. DAIRY & BAKERY
    # ==========================================
    elif any(k in q for k in ["dairy", "milk", "cheese", "paneer", "bread", "bakery", "egg"]):
        return {
            "title": "🥛 Farm Fresh Dairy, Artisan Bakery & Eggs",
            "category": "Dairy & Bakery",
            "summary": "Cold-chain transported daily essentials delivered fresh every morning:",
            "points": [
                ("Pasteurized Milk", "Full cream, toned, double toned, and lactose-free dairy milk delivered before sunrise."),
                ("Pure Malai Paneer", "Freshly prepared, ultra-soft paneer perfect for curries and protein bowls."),
                ("Whole Wheat & Multigrain Bread", "Freshly baked artisan breads, brown bread, and burger buns."),
                ("Farm Fresh Eggs", "White and brown free-range eggs rich in Vitamin B12 and Omega-3.")
            ],
            "suggested_query": "milk"
        }

    # ==========================================
    # DEFAULT / GENERAL WELCOME
    # ==========================================
    else:
        return {
            "title": "🤖 Welcome to FreshMart AI Grocery Assistant",
            "category": "General Guide",
            "summary": f"You asked: \"{question}\". I am trained to give you immediate expert guidance on groceries, nutrition, recipes, and store assistance.",
            "points": [
                ("Health & Dietary Plans", "Ask for 'foods for weight loss', 'protein rich diet', 'diabetes friendly groceries', or 'heart health'."),
                ("Meal Ideas & Cooking", "Ask for 'quick breakfast ideas', 'healthy snacks', or '15 minute meals'."),
                ("Produce & Freshness", "Ask for 'how to store vegetables fresh', 'fresh fruits recommendations', or 'pantry checklist'."),
                ("Store Assistance", "Ask about 'delivery time', 'active coupons', 'payment methods', or 'how to track orders'.")
            ],
            "tip": "Click any of the quick suggestion chips above to explore instant guidance!",
            "suggested_query": ""
        }


def index(request):
    answer = None
    user_query = ""
    matching_products = []

    if request.method == "POST":
        user_query = request.POST.get("question", "").strip()
        if user_query:
            answer = get_ai_response(user_query)

            # Look up related products in database if query has a suggested keyword
            suggested_term = answer.get("suggested_query")
            if suggested_term:
                matching_products = Product.objects.filter(
                    available=True,
                    name__icontains=suggested_term
                )[:4]
            if not matching_products:
                matching_products = Product.objects.filter(available=True)[:4]

    categories = Category.objects.filter(is_active=True)[:6]

    return render(
        request,
        "ai_assistant/index.html",
        {
            "answer": answer,
            "user_query": user_query,
            "matching_products": matching_products,
            "categories": categories,
        }
    )