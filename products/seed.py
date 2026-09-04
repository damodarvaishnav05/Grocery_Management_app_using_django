from decimal import Decimal
from categories.models import Category
from products.models import Product


def seed_all_groceries():
    """
    Seeds comprehensive grocery categories and products if database is empty or sparse.
    Every product is strictly isolated to its real-world category with dedicated images.
    """
    categories_data = [
        {
            "name": "Fresh Fruits",
            "slug": "fruits",
            "icon": "bi-apple",
            "description": "Farm-fresh fruits picked daily for sweetness and nutrition.",
            "image": "categories/360_F_300960026_7EQfwamohGMPe5UETducKqskHEZOIMqG.jpg",
        },
        {
            "name": "Fresh Vegetables",
            "slug": "vegetables",
            "icon": "bi-flower1",
            "description": "Crisp greens, root vegetables and cooking essentials fresh from local farms.",
            "image": "",
        },
        {
            "name": "Dairy, Bread & Eggs",
            "slug": "dairy-bread-eggs",
            "icon": "bi-egg-fried",
            "description": "Fresh cow milk, artisan breads, malai paneer, butter and farm eggs.",
            "image": "",
        },
        {
            "name": "Beverages & Juices",
            "slug": "beverages",
            "icon": "bi-cup-straw",
            "description": "Cold-pressed juices, premium teas, coffees, soft drinks and sparkling water.",
            "image": "categories/image_coldrinks.webp",
        },
        {
            "name": "Snacks & Munchies",
            "slug": "snacks",
            "icon": "bi-cookie",
            "description": "Crunchy roasted nuts, gourmet chips, nutritious bars and healthy bites.",
            "image": "",
        },
        {
            "name": "Bakery & Cakes",
            "slug": "bakery",
            "icon": "bi-cake2",
            "description": "Freshly baked artisan loaves, croissants, chocolate cakes and cookies.",
            "image": "categories/bakery.jpg",
        },
        {
            "name": "Pantry Staples",
            "slug": "pantry",
            "icon": "bi-basket2",
            "description": "Aromatic basmati rice, organic pulses, cold-pressed oils and whole spices.",
            "image": "",
        },
        {
            "name": "Home & Personal Care",
            "slug": "home-care",
            "icon": "bi-shield-plus",
            "description": "Household cleaners, laundry detergents, hand hygiene and body care.",
            "image": "",
        },
    ]

    category_objs = {}
    for cdata in categories_data:
        cat, _ = Category.objects.update_or_create(
            slug=cdata["slug"],
            defaults={
                "name": cdata["name"],
                "icon": cdata["icon"],
                "description": cdata["description"],
                "is_active": True,
            }
        )
        if cdata["image"] and not cat.image:
            cat.image = cdata["image"]
            cat.save()
        category_objs[cdata["slug"]] = cat

    products_data = [
        # ==========================================
        # 1. Fresh Fruits
        # ==========================================
        {
            "category": "fruits",
            "name": "Royal Gala Apples (1 kg)",
            "slug": "royal-gala-apples-1kg",
            "description": "Crisp, naturally sweet and aromatic apples imported fresh. Rich in antioxidants and dietary fiber.",
            "price": Decimal("180.00"),
            "discount_price": Decimal("149.00"),
            "stock": 45,
            "image": "products/red-apple-isolated-white-background-71475088.webp",
        },
        {
            "category": "fruits",
            "name": "Robusta Fresh Bananas (1 Dozen)",
            "slug": "robusta-fresh-bananas-1-dozen",
            "description": "Naturally ripened Robusta bananas packed with potassium and instant natural energy.",
            "price": Decimal("65.00"),
            "discount_price": Decimal("48.00"),
            "stock": 60,
            "image": "products/fresh_bananas.jpg",
        },
        {
            "category": "fruits",
            "name": "Alphonso Mangoes (Box of 6)",
            "slug": "alphonso-mangoes-box-6",
            "description": "The king of mangoes. Hand-harvested from Ratnagiri farms, golden pulped, and heavenly sweet.",
            "price": Decimal("499.00"),
            "discount_price": Decimal("399.00"),
            "stock": 25,
            "image": "products/alphonso_mangoes.jpg",
        },
        {
            "category": "fruits",
            "name": "Ruby Red Pomegranate (1 kg)",
            "slug": "ruby-red-pomegranate-1kg",
            "description": "Juicy, ruby-red arils rich in vitamin C and polyphenols. Promotes heart health and radiant skin.",
            "price": Decimal("220.00"),
            "discount_price": Decimal("185.00"),
            "stock": 35,
            "image": "products/ruby_pomegranate.jpg",
        },
        {
            "category": "fruits",
            "name": "Nagpur Sweet Oranges (1 kg)",
            "slug": "nagpur-sweet-oranges-1kg",
            "description": "Juicy Nagpur oranges with the perfect balance of sweet and tangy citrus flavors.",
            "price": Decimal("110.00"),
            "discount_price": Decimal("89.00"),
            "stock": 40,
            "image": "products/sweet_oranges.jpg",
        },
        {
            "category": "fruits",
            "name": "Fresh Green Zesty Kiwis (Pack of 3)",
            "slug": "fresh-green-zesty-kiwis-3pk",
            "description": "Nutrient-rich emerald green kiwis packed with natural Vitamin C and digestive enzymes.",
            "price": Decimal("135.00"),
            "discount_price": Decimal("109.00"),
            "stock": 40,
            "image": "products/fresh_green_kiwis.jpg",
        },

        # ==========================================
        # 2. Fresh Vegetables
        # ==========================================
        {
            "category": "vegetables",
            "name": "Farm Fresh Potatoes (2 kg)",
            "slug": "farm-fresh-potatoes-2kg",
            "description": "Unpolished, earthy farm potatoes suitable for baking, boiling, fries, and everyday curries.",
            "price": Decimal("70.00"),
            "discount_price": Decimal("54.00"),
            "stock": 80,
            "image": "products/fresh_potatoes.jpg",
        },
        {
            "category": "vegetables",
            "name": "Fresh Red Onions (2 kg)",
            "slug": "fresh-red-onions-2kg",
            "description": "Pungent, crisp and flavorful red onions essential for every kitchen base and fresh salads.",
            "price": Decimal("80.00"),
            "discount_price": Decimal("65.00"),
            "stock": 90,
            "image": "products/fresh_red_onions.jpg",
        },
        {
            "category": "vegetables",
            "name": "Vine Ripe Hybrid Tomatoes (1 kg)",
            "slug": "vine-ripe-hybrid-tomatoes-1kg",
            "description": "Juicy, firm, deep red tomatoes harvested at peak ripeness. Perfect for sauces and salads.",
            "price": Decimal("50.00"),
            "discount_price": Decimal("38.00"),
            "stock": 70,
            "image": "products/ripe_tomatoes.jpg",
        },
        {
            "category": "vegetables",
            "name": "Fresh Baby Spinach / Palak (250g)",
            "slug": "fresh-baby-spinach-250g",
            "description": "Tender hydroponic baby spinach leaves, hydro-cooled and cleaned. Rich in iron and folate.",
            "price": Decimal("35.00"),
            "discount_price": Decimal("26.00"),
            "stock": 30,
            "image": "products/baby_spinach.jpg",
        },
        {
            "category": "vegetables",
            "name": "Crunchy English Cucumbers (500g)",
            "slug": "crunchy-english-cucumbers-500g",
            "description": "Seedless, crisp and refreshing cucumbers. 96% water content for effortless hydration.",
            "price": Decimal("40.00"),
            "discount_price": Decimal("29.00"),
            "stock": 50,
            "image": "products/english_cucumbers.jpg",
        },
        {
            "category": "vegetables",
            "name": "Fresh Green Broccoli Florets (500g)",
            "slug": "fresh-green-broccoli-florets-500g",
            "description": "Crisp, antioxidant-packed tender green broccoli heads harvested fresh.",
            "price": Decimal("90.00"),
            "discount_price": Decimal("72.00"),
            "stock": 35,
            "image": "products/fresh_broccoli.jpg",
        },

        # ==========================================
        # 3. Dairy, Bread & Eggs
        # ==========================================
        {
            "category": "dairy-bread-eggs",
            "name": "Fresh Cow Milk - Full Cream (1 Litre)",
            "slug": "fresh-cow-milk-1-litre",
            "description": "Pure, pasteurized farm fresh cow milk with rich natural cream. Delivered cold daily.",
            "price": Decimal("72.00"),
            "discount_price": Decimal("66.00"),
            "stock": 50,
            "image": "products/cow_milk.jpg",
        },
        {
            "category": "dairy-bread-eggs",
            "name": "Farm Fresh White Eggs (Pack of 12)",
            "slug": "farm-fresh-white-eggs-12pk",
            "description": "Grade-A farm eggs, cleaned and tested. Packed with 6g of high-biological value protein per egg.",
            "price": Decimal("105.00"),
            "discount_price": Decimal("88.00"),
            "stock": 40,
            "image": "products/white_eggs.jpg",
        },
        {
            "category": "dairy-bread-eggs",
            "name": "Fresh Malai Paneer (200g)",
            "slug": "fresh-malai-paneer-200g",
            "description": "Melt-in-the-mouth soft cottage cheese made from 100% cow milk. Unmatched freshness.",
            "price": Decimal("115.00"),
            "discount_price": Decimal("99.00"),
            "stock": 35,
            "image": "products/malai_paneer.jpg",
        },
        {
            "category": "dairy-bread-eggs",
            "name": "100% Whole Wheat Bread (400g)",
            "slug": "100-percent-whole-wheat-bread-400g",
            "description": "Zero maida, high-fiber whole grain loaf baked fresh each dawn. Toasts to golden perfection.",
            "price": Decimal("55.00"),
            "discount_price": Decimal("48.00"),
            "stock": 30,
            "image": "products/whole_wheat_bread.jpg",
        },
        {
            "category": "dairy-bread-eggs",
            "name": "Pure Dairy Pasteurized Cream Butter (500g)",
            "slug": "pure-dairy-pasteurized-cream-butter-500g",
            "description": "Rich, creamy golden butter churned from pure cow milk cream. Lightly salted.",
            "price": Decimal("290.00"),
            "discount_price": Decimal("249.00"),
            "stock": 40,
            "image": "products/pure_dairy_butter.jpg",
        },

        # ==========================================
        # 4. Beverages & Juices
        # ==========================================
        {
            "category": "beverages",
            "name": "Thums Up Charged Soft Drink (750 ml)",
            "slug": "thums-up-charged-750ml",
            "description": "The bold, spicy and fizzy carbonated soft drink that gives you an exhilarating kick.",
            "price": Decimal("45.00"),
            "discount_price": Decimal("40.00"),
            "stock": 80,
            "image": "products/40318744_1-thums-up-soft-drink.webp",
        },
        {
            "category": "beverages",
            "name": "Cold Pressed Valencia Orange Juice (1 Litre)",
            "slug": "cold-pressed-valencia-orange-juice-1l",
            "description": "100% pure squeezed orange juice with natural pulp. Zero added sugars or preservatives.",
            "price": Decimal("150.00"),
            "discount_price": Decimal("129.00"),
            "stock": 25,
            "image": "products/orange_juice.jpg",
        },
        {
            "category": "beverages",
            "name": "Natural Tender Coconut Water (Pack of 2)",
            "slug": "natural-tender-coconut-water-2pk",
            "description": "Naturally electrolyte-rich fresh coconut water. Restores hydration instantly after workouts.",
            "price": Decimal("120.00"),
            "discount_price": Decimal("99.00"),
            "stock": 30,
            "image": "products/tender_coconut.jpg",
        },
        {
            "category": "beverages",
            "name": "Sprite",
            "slug": "sprite",
            "description": "Crisp, clean and refreshing lemon-lime flavored carbonated soda.",
            "price": Decimal("45.00"),
            "discount_price": Decimal("40.00"),
            "stock": 70,
            "image": "products/images_4_DFLE0QW.jpg",
        },
        {
            "category": "beverages",
            "name": "Fanta",
            "slug": "fanta",
            "description": "Bright, bubbly orange flavored soft drink bursting with fruity zest.",
            "price": Decimal("45.00"),
            "discount_price": Decimal("40.00"),
            "stock": 65,
            "image": "products/images_5_L7fwxu4.jpg",
        },
        {
            "category": "beverages",
            "name": "Classic Chilled Coca-Cola (300 ml Can)",
            "slug": "tumsup",
            "description": "Refreshing, effervescent Coca-Cola served ice-cold. Real magic in every sip.",
            "price": Decimal("40.00"),
            "discount_price": Decimal("35.00"),
            "stock": 75,
            "image": "products/images_3.jpg",
        },

        # ==========================================
        # 5. Bakery & Cakes
        # ==========================================
        {
            "category": "bakery",
            "name": "Cream Drop Chocolate Truffle Cake (500g)",
            "slug": "cream-drop-chocolate-truffle-cake-500g",
            "description": "Decadent Dutch cocoa sponge layered with silky chocolate ganache and chocolate curls.",
            "price": Decimal("450.00"),
            "discount_price": Decimal("389.00"),
            "stock": 15,
            "image": "products/cream-drop-chocolate-cake_1.webp",
        },
        {
            "category": "bakery",
            "name": "Artisan Butter Croissants (Pack of 2)",
            "slug": "artisan-butter-croissants-pack-2",
            "description": "Flaky, buttery French-style croissants layered with golden crispness outside and feather-soft inside.",
            "price": Decimal("130.00"),
            "discount_price": Decimal("105.00"),
            "stock": 20,
            "image": "products/artisan_croissants.jpg",
        },
        {
            "category": "bakery",
            "name": "Double Chocochip Soft Bakery Cookies (Box of 6)",
            "slug": "double-chocochip-soft-bakery-cookies-6pk",
            "description": "Freshly baked melt-in-mouth chewy cookies loaded with dark and milk chocolate chips.",
            "price": Decimal("160.00"),
            "discount_price": Decimal("129.00"),
            "stock": 30,
            "image": "products/double_chocochip_cookies.jpg",
        },
        {
            "category": "bakery",
            "name": "Strawberry Cake",
            "slug": "strawberry-cake",
            "description": "Fluffy vanilla sponge cake layered with fresh strawberry compote and whipped cream.",
            "price": Decimal("350.00"),
            "discount_price": Decimal("290.00"),
            "stock": 15,
            "image": "products/images.jpg",
        },
        {
            "category": "bakery",
            "name": "Choclate Cake",
            "slug": "choclate-cake",
            "description": "Rich dark chocolate layer cake topped with chocolate glaze and shavings.",
            "price": Decimal("350.00"),
            "discount_price": Decimal("290.00"),
            "stock": 20,
            "image": "products/cream-drop-chocolate-cake_1.webp",
        },

        # ==========================================
        # 6. Home & Personal Care
        # ==========================================
        {
            "category": "home-care",
            "name": "Ariel Complete Detergent Powder (4 kg)",
            "slug": "ariel-complete-detergent-powder-4kg",
            "description": "Deep stain removal in just 1 wash with freshness technology. Safe for whites and colors.",
            "price": Decimal("499.00"),
            "discount_price": Decimal("425.00"),
            "stock": 40,
            "image": "products/4-detergent-powder-complete-4kg-ariel-original-imafumtq2vbyqygm.webp",
        },
        {
            "category": "home-care",
            "name": "Ariel Powder",
            "slug": "ariel-powder",
            "description": "Advanced enzyme formula that cuts through tough dirt, grease and cuff grime.",
            "price": Decimal("150.00"),
            "discount_price": Decimal("130.00"),
            "stock": 35,
            "image": "products/4-detergent-powder-complete-4kg-ariel-original-imafumtq2vbyqygm.webp",
        },
        {
            "category": "home-care",
            "name": "Rin Powder",
            "slug": "rin-powder",
            "description": "Dazzling brightness for whites and daily laundry with anti-greying protection.",
            "price": Decimal("90.00"),
            "discount_price": Decimal("75.00"),
            "stock": 45,
            "image": "products/images_10_vUjaneo.jpg",
        },
        {
            "category": "home-care",
            "name": "Surf Excel Quick Wash",
            "slug": "surf-excel-quick-wash",
            "description": "Superior stain removal in half the time. Dissolves completely without residue.",
            "price": Decimal("180.00"),
            "discount_price": Decimal("155.00"),
            "stock": 40,
            "image": "products/103678928_11.webp",
        },
        {
            "category": "home-care",
            "name": "Wheel Powder",
            "slug": "wheel-powder",
            "description": "Lemon and floral power for effective daily fabric wash and long-lasting freshness.",
            "price": Decimal("50.00"),
            "discount_price": Decimal("42.00"),
            "stock": 60,
            "image": "products/images_9_0Jzi49v.jpg",
        },

        # ==========================================
        # 7. Pantry Staples
        # ==========================================
        {
            "category": "pantry",
            "name": "Daawat Rozana Super Basmati Rice (1 kg)",
            "slug": "daawat-rozana-super-basmati-rice-1kg",
            "description": "Aromatic, extra-long slender grains aged to perfection. Fluffy, non-sticky and royal aroma.",
            "price": Decimal("165.00"),
            "discount_price": Decimal("139.00"),
            "stock": 60,
            "image": "products/basmati_rice.jpg",
        },
        {
            "category": "pantry",
            "name": "Organic Unpolished Toor Dal (1 kg)",
            "slug": "organic-unpolished-toor-dal-1kg",
            "description": "Pesticide-free yellow pigeon peas unpolished to retain natural fiber and protein.",
            "price": Decimal("190.00"),
            "discount_price": Decimal("165.00"),
            "stock": 50,
            "image": "products/toor_dal.jpg",
        },
        {
            "category": "pantry",
            "name": "Sunflower Valley Pure Refined Sunflower Oil (1 Litre)",
            "slug": "sunflower-valley-refined-sunflower-oil-1l",
            "description": "Light, healthy pure refined sunflower cooking oil enriched with Vitamins A & D.",
            "price": Decimal("175.00"),
            "discount_price": Decimal("145.00"),
            "stock": 55,
            "image": "products/sunflower_oil.jpg",
        },
        {
            "category": "pantry",
            "name": "Ashirvad Whole Wheat Chakki Atta (5 kg)",
            "slug": "ashirvad-whole-wheat-chakki-atta-5kg",
            "description": "100% whole wheat stone ground chakki atta. Yields soft, fluffy, fiber-rich rotis.",
            "price": Decimal("275.00"),
            "discount_price": Decimal("239.00"),
            "stock": 45,
            "image": "products/whole_wheat_chakki_atta.jpg",
        },
        {
            "category": "pantry",
            "name": "Tata Pure Vacuum Evaporated Iodized Salt (1 kg)",
            "slug": "tata-pure-iodized-salt-1kg",
            "description": "India trusted vacuum-evaporated table salt for healthy iodine balance.",
            "price": Decimal("28.00"),
            "discount_price": Decimal("24.00"),
            "stock": 100,
            "image": "products/iodized_salt.jpg",
        },

        # ==========================================
        # 8. Snacks & Munchies
        # ==========================================
        {
            "category": "snacks",
            "name": "California Roasted & Salted Almonds (250g)",
            "slug": "california-roasted-salted-almonds-250g",
            "description": "Crunchy whole California almonds slow-roasted and lightly sprinkled with Himalayan pink salt.",
            "price": Decimal("320.00"),
            "discount_price": Decimal("269.00"),
            "stock": 35,
            "image": "products/roasted_almonds.jpg",
        },
        {
            "category": "snacks",
            "name": "All-Natural Crunchy Peanut Butter (350g)",
            "slug": "all-natural-crunchy-peanut-butter-350g",
            "description": "100% roasted peanuts with crunchy bits. Zero hydrogenated oils, zero refined sugar.",
            "price": Decimal("195.00"),
            "discount_price": Decimal("165.00"),
            "stock": 40,
            "image": "products/peanut_butter.jpg",
        },
        {
            "category": "snacks",
            "name": "Harvest Crisps Golden Salted Potato Chips (200g)",
            "slug": "harvest-crisps-golden-salted-potato-chips-200g",
            "description": "Crisp, golden-sliced potatoes lightly dusted with natural sea salt. Zero trans-fat snack.",
            "price": Decimal("95.00"),
            "discount_price": Decimal("79.00"),
            "stock": 60,
            "image": "products/harvest_crisp_chips.jpg",
        },
        {
            "category": "snacks",
            "name": "Dark Chocolate & Roasted Almond Granola Bars (Pack of 4)",
            "slug": "dark-chocolate-almond-granola-bars-4pk",
            "description": "Wholesome rolled oats with Belgian dark chocolate chips and California roasted almonds.",
            "price": Decimal("199.00"),
            "discount_price": Decimal("159.00"),
            "stock": 40,
            "image": "products/dark_chocolate_granola_bars.jpg",
        },
        {
            "category": "snacks",
            "name": "Crispy Masala Bhujia Sev (200g)",
            "slug": "crispy-masala-bhujia-sev-200g",
            "description": "Traditional crunchy moth bean & gram flour noodles tossed in tangy aromatic spices.",
            "price": Decimal("60.00"),
            "discount_price": Decimal("49.00"),
            "stock": 50,
            "image": "products/bhujia_sev.jpg",
        },
    ]

    for pdata in products_data:
        cat = category_objs.get(pdata["category"])
        if not cat:
            continue

        Product.objects.update_or_create(
            slug=pdata["slug"],
            defaults={
                "category": cat,
                "name": pdata["name"],
                "description": pdata["description"],
                "price": pdata["price"],
                "discount_price": pdata["discount_price"],
                "stock": pdata["stock"],
                "available": True,
                "image": pdata["image"],
            }
        )
