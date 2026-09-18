from decimal import Decimal
import os
import glob
from django.core.management.base import BaseCommand
from django.conf import settings
from categories.models import Category
from products.models import Product
from PIL import Image, ImageDraw


def clean_to_pure_white_canvas(source_path, target_path, canvas_size=(600, 600), pad=35):
    """
    Cleans source image to an authentic pure white (#FFFFFF) background
    and centers the product on a square canvas.
    """
    if not os.path.exists(source_path):
        return False

    try:
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        img = Image.open(source_path).convert('RGBA')
        w, h = img.size

        # Floodfill from all 4 corners if light/near-white
        for corner in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
            c_val = img.getpixel(corner)
            if c_val[3] > 0 and (c_val[0] > 215 and c_val[1] > 215 and c_val[2] > 215):
                ImageDraw.floodfill(img, corner, (255, 255, 255, 0), thresh=40)

        bbox = img.getbbox()
        if bbox:
            img = img.crop(bbox)

        canvas = Image.new('RGB', canvas_size, (255, 255, 255))
        max_w = canvas_size[0] - pad * 2
        max_h = canvas_size[1] - pad * 2
        img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)

        x = (canvas_size[0] - img.width) // 2
        y = (canvas_size[1] - img.height) // 2
        canvas.paste(img, (x, y), img)

        canvas.save(target_path, 'WEBP', quality=92)
        return True
    except Exception as e:
        print(f"Error processing {source_path}: {e}")
        return False


class Command(BaseCommand):
    help = "Seeds authentic category-wise grocery products with real pure white background images"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding authentic category-wise groceries..."))

        brain_dir = r"C:\Users\DAMODAR\.gemini\antigravity\brain\ab9c0a5d-b4d9-40a6-a55f-8d9104fe85fd"
        media_products_dir = os.path.join(settings.MEDIA_ROOT, "products")
        os.makedirs(media_products_dir, exist_ok=True)

        categories_data = [
            {
                "name": "Dairy, Bread & Eggs",
                "slug": "dairy-bread-eggs",
                "icon": "bi-egg-fried",
                "description": "Fresh milk, creamy butter, soft malai paneer, artisan bread and farm eggs.",
                "image": "",
            },
            {
                "name": "Fresh Fruits",
                "slug": "fruits",
                "icon": "bi-apple",
                "description": "Farm-picked apples, bananas, sweet oranges, and fresh seasonal fruits.",
                "image": "categories/360_F_300960026_7EQfwamohGMPe5UETducKqskHEZOIMqG.jpg",
            },
            {
                "name": "Fresh Vegetables",
                "slug": "vegetables",
                "icon": "bi-flower1",
                "description": "Crisp farm potatoes, red onions, ripe tomatoes, fresh spinach and greens.",
                "image": "",
            },
            {
                "name": "Snacks & Munchies",
                "slug": "snacks",
                "icon": "bi-cookie",
                "description": "Lay's chips, Kurkure, Haldiram's bhujia, chocolates, and crunchy namkeen.",
                "image": "",
            },
            {
                "name": "Beverages & Juices",
                "slug": "beverages",
                "icon": "bi-cup-straw",
                "description": "Chilled soft drinks, Maaza, Tata Tea Gold, Nescafé coffee, and juices.",
                "image": "categories/image_coldrinks.webp",
            },
            {
                "name": "Bakery & Cakes",
                "slug": "bakery",
                "icon": "bi-cake2",
                "description": "Artisan chocolate cakes, buttery croissants, soft cookies and fresh buns.",
                "image": "categories/bakery.jpg",
            },
            {
                "name": "Pantry Staples",
                "slug": "pantry",
                "icon": "bi-basket2",
                "description": "Maggi noodles, Aashirvaad Sharbati Atta, Fortune sunflower oil, basmati rice.",
                "image": "",
            },
            {
                "name": "Home & Personal Care",
                "slug": "home-care",
                "icon": "bi-shield-plus",
                "description": "Dettol antiseptic, Colgate MaxFresh toothpaste, Surf Excel and household hygiene.",
                "image": "",
            },
        ]

        category_objs = {}
        for cdata in categories_data:
            cat, created = Category.objects.update_or_create(
                slug=cdata["slug"],
                defaults={
                    "name": cdata["name"],
                    "icon": cdata["icon"],
                    "description": cdata["description"],
                    "is_active": True,
                },
            )
            if cdata["image"] and not cat.image:
                cat.image = cdata["image"]
                cat.save()
            category_objs[cdata["slug"]] = cat

        # Helper to find source image path in brain dir or media/products
        def find_source_image(candidates):
            for cand in candidates:
                # Check in brain dir
                p_brain = os.path.join(brain_dir, cand)
                if os.path.exists(p_brain):
                    return p_brain
                # Check with glob in brain dir
                g_brain = glob.glob(os.path.join(brain_dir, f"{cand}*"))
                if g_brain:
                    return g_brain[0]
                # Check in media/products
                p_media = os.path.join(media_products_dir, cand)
                if os.path.exists(p_media):
                    return p_media
            return None

        # Comprehensive, accurate category-wise product list
        products_data = [
            # ==========================================
            # 1. DAIRY, BREAD & EGGS
            # ==========================================
            {
                "category": "dairy-bread-eggs",
                "name": "Amul Pasteurised Salted Butter (500g)",
                "slug": "amul-pasteurised-butter-500g",
                "description": "Delicious, creamy salted butter made from pure cow and buffalo milk. Utterly butterly delicious.",
                "price": Decimal("295.00"),
                "discount_price": Decimal("285.00"),
                "stock": 50,
                "barcode": "8901262010016",
                "source_candidates": ["amul_butter_1789753416524.jpg", "amul_butter_1788431270910.jpg", "pure_dairy_butter.jpg"],
            },
            {
                "category": "dairy-bread-eggs",
                "name": "Amul Taaza Homogenised Toned Milk (1 Litre)",
                "slug": "amul-taaza-toned-milk-1l",
                "description": "Pasteurised and UHT treated toned milk. Zero preservatives, rich in protein, calcium and natural vitamins.",
                "price": Decimal("78.00"),
                "discount_price": Decimal("74.00"),
                "stock": 60,
                "barcode": "8901262070010",
                "source_candidates": ["amul_taaza_milk_1789753715052.jpg", "cow_milk.jpg", "cow_milk_1788517839086.jpg"],
            },
            {
                "category": "dairy-bread-eggs",
                "name": "Mother Dairy Classic Malai Paneer (200g)",
                "slug": "mother-dairy-classic-malai-paneer-200g",
                "description": "Soft, melt-in-mouth cottage cheese crafted from pure milk. Rich in calcium and dairy protein.",
                "price": Decimal("105.00"),
                "discount_price": Decimal("92.00"),
                "stock": 45,
                "barcode": "8901648000716",
                "source_candidates": ["malai_paneer_1788518019449.jpg", "malai_paneer.jpg"],
            },
            {
                "category": "dairy-bread-eggs",
                "name": "Britannia 100% Whole Wheat Bread (400g)",
                "slug": "britannia-100-whole-wheat-bread-400g",
                "description": "Nutritious whole wheat slices baked fresh daily. High in dietary fiber with zero trans-fats.",
                "price": Decimal("55.00"),
                "discount_price": Decimal("50.00"),
                "stock": 40,
                "barcode": "8901063142277",
                "source_candidates": ["whole_wheat_bread_1788518042779.jpg", "whole_wheat_bread.jpg"],
            },
            {
                "category": "dairy-bread-eggs",
                "name": "Farm Fresh White Table Eggs (Pack of 12)",
                "slug": "farm-fresh-white-eggs-12",
                "description": "Nutritious, protein-rich white table eggs from healthy grain-fed farm poultry. Safe, clean and hygienic.",
                "price": Decimal("110.00"),
                "discount_price": Decimal("88.00"),
                "stock": 55,
                "barcode": "8901030000012",
                "source_candidates": ["white_eggs_1788517861952.jpg", "white_eggs.jpg"],
            },
            {
                "category": "dairy-bread-eggs",
                "name": "Fresh Cow Milk - Full Cream (1 Litre)",
                "slug": "fresh-cow-milk-full-cream-1l",
                "description": "Fresh, wholesome full cream cow milk delivered chilled from dairy farms. Pure taste and natural nutrition.",
                "price": Decimal("72.00"),
                "discount_price": Decimal("66.00"),
                "stock": 50,
                "barcode": "8901030000013",
                "source_candidates": ["cow_milk_1788517839086.jpg", "cow_milk.jpg"],
            },

            # ==========================================
            # 2. FRESH FRUITS
            # ==========================================
            {
                "category": "fruits",
                "name": "Royal Gala Crisp Red Apples (1 kg)",
                "slug": "royal-gala-apples-1kg",
                "description": "Crisp, naturally sweet and aromatic apples imported fresh. Rich in natural antioxidants and dietary fiber.",
                "price": Decimal("180.00"),
                "discount_price": Decimal("149.00"),
                "stock": 45,
                "barcode": "8901030000021",
                "source_candidates": ["red-apple-isolated-white-background-71475088.webp"],
            },
            {
                "category": "fruits",
                "name": "Robusta Fresh Bananas (1 Dozen)",
                "slug": "robusta-fresh-bananas-1-dozen",
                "description": "Fresh golden bananas packed with potassium, energy, and natural fruit sugars. Perfectly ripened.",
                "price": Decimal("65.00"),
                "discount_price": Decimal("48.00"),
                "stock": 60,
                "barcode": "8901030000022",
                "source_candidates": ["fresh_bananas_1788517620191.jpg", "fresh_bananas.jpg"],
            },
            {
                "category": "fruits",
                "name": "Nagpur Fresh Sweet Oranges (1 kg)",
                "slug": "nagpur-sweet-oranges-1kg",
                "description": "Juicy, citrusy sweet oranges directly from Nagpur orchards. Rich in natural Vitamin C and immunity boosters.",
                "price": Decimal("110.00"),
                "discount_price": Decimal("89.00"),
                "stock": 40,
                "barcode": "8901030000023",
                "source_candidates": ["sweet_oranges_1788517643208.jpg", "sweet_oranges.jpg"],
            },
            {
                "category": "fruits",
                "name": "Ruby Red Ripe Pomegranate (1 kg)",
                "slug": "ruby-red-pomegranate-1kg",
                "description": "Sweet, vibrant ruby-red pomegranate pearls loaded with polyphenols and vital minerals.",
                "price": Decimal("220.00"),
                "discount_price": Decimal("185.00"),
                "stock": 35,
                "barcode": "8901030000024",
                "source_candidates": ["ruby_pomegranate_1788517670269.jpg", "ruby_pomegranate.jpg"],
            },
            {
                "category": "fruits",
                "name": "Ratnagiri Alphonso Mangoes (Box of 6)",
                "slug": "alphonso-mangoes-box-6",
                "description": "The king of mangoes! Handpicked GI-tagged Ratnagiri Alphonso mangoes with divine aroma and luscious sweetness.",
                "price": Decimal("499.00"),
                "discount_price": Decimal("399.00"),
                "stock": 25,
                "barcode": "8901030000025",
                "source_candidates": ["alphonso_mangoes_1788517594053.jpg", "alphonso_mangoes.jpg"],
            },
            {
                "category": "fruits",
                "name": "Fresh Zesty Green Kiwis (Pack of 3)",
                "slug": "fresh-green-kiwis-pack-3",
                "description": "Tangy-sweet imported green kiwis packed with digestive enzymes, folate, and Vitamin C.",
                "price": Decimal("135.00"),
                "discount_price": Decimal("109.00"),
                "stock": 35,
                "barcode": "8901030000026",
                "source_candidates": ["fresh_kiwis_1788432323792.jpg", "fresh_green_kiwis.jpg"],
            },

            # ==========================================
            # 3. FRESH VEGETABLES
            # ==========================================
            {
                "category": "vegetables",
                "name": "Farm Fresh Golden Potatoes (2 kg)",
                "slug": "farm-fresh-potatoes-2kg",
                "description": "Sun-cured golden potatoes ideal for daily curries, crispy fries, aloo parathas and roasting.",
                "price": Decimal("70.00"),
                "discount_price": Decimal("54.00"),
                "stock": 70,
                "barcode": "8901030000031",
                "source_candidates": ["fresh_potatoes_1788517702228.jpg", "fresh_potatoes.jpg"],
            },
            {
                "category": "vegetables",
                "name": "Fresh Red Nasik Onions (2 kg)",
                "slug": "fresh-red-onions-2kg",
                "description": "Crisp, pungent red onions harvested in Nasik. Essential base for rich Indian gravies, tadka and salads.",
                "price": Decimal("80.00"),
                "discount_price": Decimal("65.00"),
                "stock": 75,
                "barcode": "8901030000032",
                "source_candidates": ["red_onions_1788517727313.jpg", "fresh_red_onions.jpg"],
            },
            {
                "category": "vegetables",
                "name": "Vine Ripe Hybrid Tomatoes (1 kg)",
                "slug": "vine-ripe-tomatoes-1kg",
                "description": "Juicy, firm, farm-plucked red tomatoes rich in lycopene and tangy flavor for gravies and soups.",
                "price": Decimal("50.00"),
                "discount_price": Decimal("38.00"),
                "stock": 65,
                "barcode": "8901030000033",
                "source_candidates": ["ripe_tomatoes_1788517751196.jpg", "ripe_tomatoes.jpg"],
            },
            {
                "category": "vegetables",
                "name": "Fresh Tender Baby Spinach / Palak (250g Bunch)",
                "slug": "fresh-baby-spinach-250g",
                "description": "Tender hydroponic green spinach leaves. Washed, crisp, iron-packed and ready to cook.",
                "price": Decimal("35.00"),
                "discount_price": Decimal("26.00"),
                "stock": 50,
                "barcode": "8901030000034",
                "source_candidates": ["baby_spinach_1788517779955.jpg", "baby_spinach.jpg"],
            },
            {
                "category": "vegetables",
                "name": "Crunchy English Cucumbers (500g)",
                "slug": "english-cucumbers-500g",
                "description": "Crisp, thin-skinned seedless cucumbers. Refreshing, hydrating and perfect for summer salads.",
                "price": Decimal("40.00"),
                "discount_price": Decimal("29.00"),
                "stock": 45,
                "barcode": "8901030000035",
                "source_candidates": ["english_cucumbers_1788517816337.jpg", "english_cucumbers.jpg"],
            },
            {
                "category": "vegetables",
                "name": "Fresh Green Broccoli Florets (500g)",
                "slug": "fresh-green-broccoli-500g",
                "description": "Dense, crisp green broccoli florets packed with sulforaphane, fiber, and immunity vitamins.",
                "price": Decimal("90.00"),
                "discount_price": Decimal("72.00"),
                "stock": 40,
                "barcode": "8901030000036",
                "source_candidates": ["fresh_broccoli_1788431236005.jpg", "fresh_broccoli.jpg"],
            },

            # ==========================================
            # 4. SNACKS & MUNCHIES
            # ==========================================
            {
                "category": "snacks",
                "name": "Lay's India's Magic Masala Potato Chips (50g)",
                "slug": "lays-magic-masala-50g",
                "description": "Crispy golden potato chips tossed in irresistible exotic Indian aromatic spices. Classic teatime snack.",
                "price": Decimal("20.00"),
                "discount_price": Decimal("20.00"),
                "stock": 80,
                "barcode": "8901491502016",
                "source_candidates": ["lays_magic_masala_1789753456476.jpg", "lays_chips_1788431096358.jpg", "harvest_crisp_chips.jpg"],
            },
            {
                "category": "snacks",
                "name": "Kurkure Masala Munch Crunchy Namkeen (80g)",
                "slug": "kurkure-masala-munch-80g",
                "description": "Collet snack made with rice, corn and dal, coated in zesty chatpata Indian masala flavor.",
                "price": Decimal("20.00"),
                "discount_price": Decimal("20.00"),
                "stock": 80,
                "barcode": "8901491101837",
                "source_candidates": ["kurkure_masala_1789753475846.jpg"],
            },
            {
                "category": "snacks",
                "name": "Cadbury Dairy Milk Silk Chocolate Bar (150g)",
                "slug": "cadbury-dairy-milk-silk-150g",
                "description": "Velvety, creamy smooth milk chocolate made from the finest cocoa. Melts gracefully in every bite.",
                "price": Decimal("185.00"),
                "discount_price": Decimal("165.00"),
                "stock": 45,
                "barcode": "7622201402242",
                "source_candidates": ["cadbury_dairy_milk_silk_1789753499077.jpg"],
            },
            {
                "category": "snacks",
                "name": "Lay's Classic Salted Potato Chips (50g)",
                "slug": "lays-classic-salted-chips-50g",
                "description": "Thin, crispy golden sliced potatoes delicately sprinkled with clean sea salt. Pure crisp perfection.",
                "price": Decimal("20.00"),
                "discount_price": Decimal("20.00"),
                "stock": 70,
                "barcode": "8901030000041",
                "source_candidates": ["lays_chips_1788431096358.jpg", "harvest_crisp_chips.jpg"],
            },
            {
                "category": "snacks",
                "name": "Haldiram's Crispy Masala Bhujia Sev (200g)",
                "slug": "crispy-masala-bhujia-sev-200g",
                "description": "Crispy moth bean and chickpea noodles seasoned with authentic spices. The quintessential Indian namkeen.",
                "price": Decimal("60.00"),
                "discount_price": Decimal("49.00"),
                "stock": 65,
                "barcode": "8904004400731",
                "source_candidates": ["bhujia_sev.jpg"],
            },
            {
                "category": "snacks",
                "name": "California Roasted & Salted Almonds (250g)",
                "slug": "california-roasted-salted-almonds-250g",
                "description": "Crunchy whole California almonds slow-roasted and lightly sprinkled with pink salt. Healthy superfood.",
                "price": Decimal("320.00"),
                "discount_price": Decimal("269.00"),
                "stock": 40,
                "barcode": "8901030000042",
                "source_candidates": ["roasted_almonds.jpg"],
            },
            {
                "category": "snacks",
                "name": "All-Natural Crunchy Peanut Butter (350g)",
                "slug": "all-natural-crunchy-peanut-butter-350g",
                "description": "100% roasted peanuts with crunchy bits. Zero hydrogenated oils, zero refined sugar. 30% natural protein.",
                "price": Decimal("195.00"),
                "discount_price": Decimal("165.00"),
                "stock": 40,
                "barcode": "8901030000043",
                "source_candidates": ["peanut_butter.jpg"],
            },
            {
                "category": "snacks",
                "name": "Dark Chocolate & Almond Granola Bars (Pack of 4)",
                "slug": "dark-chocolate-granola-bars-pack-4",
                "description": "Wholesome rolled oats, roasted Californian almonds and dark chocolate chunks for on-the-go energy.",
                "price": Decimal("199.00"),
                "discount_price": Decimal("159.00"),
                "stock": 35,
                "barcode": "8901030000044",
                "source_candidates": ["granola_bars_1788432238100.jpg", "dark_chocolate_granola_bars.jpg"],
            },

            # ==========================================
            # 5. BEVERAGES & JUICES
            # ==========================================
            {
                "category": "beverages",
                "name": "Classic Chilled Coca-Cola (300 ml Can)",
                "slug": "classic-coca-cola-can-300ml",
                "description": "Original sparkling cola refreshment served crisp and ice-cold. Perfect fizzy thirst-quencher.",
                "price": Decimal("40.00"),
                "discount_price": Decimal("38.00"),
                "stock": 80,
                "barcode": "5449000000996",
                "source_candidates": ["images_3.jpg", "images_3_ul3C26A.jpg"],
            },
            {
                "category": "beverages",
                "name": "Thums Up Charged Soft Drink (750 ml)",
                "slug": "thums-up-charged-soft-drink-750ml",
                "description": "Taste the thunder! Bold, extra-spicy and fizzy Indian cola with a refreshing kick.",
                "price": Decimal("45.00"),
                "discount_price": Decimal("40.00"),
                "stock": 65,
                "barcode": "8901764012211",
                "source_candidates": ["40318744_1-thums-up-soft-drink.webp"],
            },
            {
                "category": "beverages",
                "name": "Sprite Refreshing Lemon-Lime (750 ml)",
                "slug": "sprite-refreshing-lime-750ml",
                "description": "Clear, crisp, caffeine-free sparkling drink bursting with 100% natural lemon-lime flavor.",
                "price": Decimal("45.00"),
                "discount_price": Decimal("40.00"),
                "stock": 60,
                "barcode": "8901764022210",
                "source_candidates": ["images_4.jpg", "images_4_DFLE0QW.jpg"],
            },
            {
                "category": "beverages",
                "name": "Fanta Sparkling Orange Soft Drink (750 ml)",
                "slug": "fanta-orange-flavour-750ml",
                "description": "Bright, bubbly and zesty orange soda that brings fun and fruity refreshment to any moment.",
                "price": Decimal("45.00"),
                "discount_price": Decimal("40.00"),
                "stock": 55,
                "barcode": "8901764032219",
                "source_candidates": ["images_5.jpg", "images_5_L7fwxu4.jpg"],
            },
            {
                "category": "beverages",
                "name": "Maaza Real Alphonso Mango Drink (1.2 Litre)",
                "slug": "maaza-mango-juice-1200ml",
                "description": "Rich, luscious mango nectar prepared from succulent Alphonso mango pulp. Thick and delicious.",
                "price": Decimal("75.00"),
                "discount_price": Decimal("68.00"),
                "stock": 50,
                "barcode": "8901764042218",
                "source_candidates": ["maaza_mango_drink_1789753679954.jpg"],
            },
            {
                "category": "beverages",
                "name": "Tata Tea Gold Pure Darjeeling Leaf Tea (500g)",
                "slug": "tata-tea-gold-leaf-500g",
                "description": "Exquisite blend of fine Assam CTC tea gently pressed with gently rolled long Darjeeling tea leaves.",
                "price": Decimal("340.00"),
                "discount_price": Decimal("295.00"),
                "stock": 45,
                "barcode": "8901052002016",
                "source_candidates": ["tata_tea_gold_1789753625881.jpg"],
            },
            {
                "category": "beverages",
                "name": "Nescafé Classic 100% Pure Instant Coffee (100g Jar)",
                "slug": "nescafe-classic-instant-coffee-100g",
                "description": "Rich aroma and distinctive roasted coffee flavor extracted from premium Robusta beans.",
                "price": Decimal("360.00"),
                "discount_price": Decimal("320.00"),
                "stock": 40,
                "barcode": "8901058852370",
                "source_candidates": ["nescafe_classic_1789753651625.jpg"],
            },
            {
                "category": "beverages",
                "name": "Cold Pressed Valencia Orange Juice (1 Litre)",
                "slug": "cold-pressed-valencia-orange-juice-1l",
                "description": "100% raw, unpasteurised and cold-pressed Valencia oranges. Zero added sugar or water.",
                "price": Decimal("150.00"),
                "discount_price": Decimal("129.00"),
                "stock": 35,
                "barcode": "8901030000051",
                "source_candidates": ["orange_juice.jpg"],
            },
            {
                "category": "beverages",
                "name": "Natural Tender Coconut Water (Pack of 2)",
                "slug": "natural-tender-coconut-water-pack-2",
                "description": "Pure, naturally isotonic electrolytes tapped fresh from young green coastal coconuts.",
                "price": Decimal("120.00"),
                "discount_price": Decimal("99.00"),
                "stock": 40,
                "barcode": "8901030000052",
                "source_candidates": ["tender_coconut.jpg"],
            },

            # ==========================================
            # 6. BAKERY & CAKES
            # ==========================================
            {
                "category": "bakery",
                "name": "Cream Drop Chocolate Truffle Cake (500g)",
                "slug": "cream-drop-chocolate-truffle-cake-500g",
                "description": "Decadent layered dark chocolate sponge cake enveloped in silky ganache and hand-crafted glaze.",
                "price": Decimal("450.00"),
                "discount_price": Decimal("389.00"),
                "stock": 25,
                "barcode": "8901030000061",
                "source_candidates": ["cream-drop-chocolate-cake_1.webp"],
            },
            {
                "category": "bakery",
                "name": "Artisan Butter Flaky Croissants (Pack of 2)",
                "slug": "artisan-butter-croissants-pack-2",
                "description": "French-style golden flaky croissants rolled with pure butter and baked until crisp and golden brown.",
                "price": Decimal("130.00"),
                "discount_price": Decimal("105.00"),
                "stock": 30,
                "barcode": "8901030000062",
                "source_candidates": ["artisan_croissants_1788429921256.jpg", "artisan_croissants.jpg"],
            },
            {
                "category": "bakery",
                "name": "Double Chocochip Soft Bakery Cookies (Box of 6)",
                "slug": "double-chocochip-bakery-cookies-box-6",
                "description": "Rich cocoa cookies generously studded with Belgian dark and milk chocolate chips. Soft-baked center.",
                "price": Decimal("160.00"),
                "discount_price": Decimal("129.00"),
                "stock": 35,
                "barcode": "8901030000063",
                "source_candidates": ["chocochip_cookies_1788431128314.jpg", "double_chocochip_cookies.jpg"],
            },

            # ==========================================
            # 7. PANTRY STAPLES
            # ==========================================
            {
                "category": "pantry",
                "name": "Maggi 2-Minute Masala Instant Noodles (70g Pack)",
                "slug": "maggi-2-minute-masala-noodles-70g",
                "description": "India's beloved instant noodles made with quality roast spices and fortified with iron and goodness.",
                "price": Decimal("14.00"),
                "discount_price": Decimal("14.00"),
                "stock": 95,
                "barcode": "8901058000306",
                "source_candidates": ["maggi_noodles_1789753434952.jpg"],
            },
            {
                "category": "pantry",
                "name": "Aashirvaad Superior MP Sharbati Whole Wheat Atta (5 kg)",
                "slug": "aashirvaad-superior-mp-atta-5kg",
                "description": "100% pure whole wheat grain harvested in Madhya Pradesh soils. Kneads into extra-soft and fluffy rotis.",
                "price": Decimal("280.00"),
                "discount_price": Decimal("245.00"),
                "stock": 60,
                "barcode": "8901725016838",
                "source_candidates": ["aashirvaad_atta_1789753569985.jpg", "wheat_flour_1788432281528.jpg", "whole_wheat_chakki_atta.jpg"],
            },
            {
                "category": "pantry",
                "name": "Fortune Sunlite Refined Sunflower Oil (1 Litre Pouch)",
                "slug": "fortune-sunlite-sunflower-oil-1l",
                "description": "Light, healthy and easy to digest refined sunflower oil enriched with natural Vitamins A, D & E.",
                "price": Decimal("165.00"),
                "discount_price": Decimal("138.00"),
                "stock": 65,
                "barcode": "8906007280242",
                "source_candidates": ["fortune_sunflower_oil_1789753596370.jpg", "sunflower_oil_1788431304252.jpg", "sunflower_oil.jpg"],
            },
            {
                "category": "pantry",
                "name": "Daawat Rozana Super Basmati Rice (1 kg)",
                "slug": "daawat-rozana-super-basmati-rice-1kg",
                "description": "Aromatic, extra-long slender grains aged to perfection. Fluffy, non-sticky and royal aroma.",
                "price": Decimal("165.00"),
                "discount_price": Decimal("139.00"),
                "stock": 55,
                "barcode": "8901537001013",
                "source_candidates": ["basmati_rice.jpg"],
            },
            {
                "category": "pantry",
                "name": "Organic Unpolished Toor Dal (1 kg)",
                "slug": "organic-unpolished-toor-dal-1kg",
                "description": "Pesticide-free yellow pigeon peas unpolished to retain 100% natural fiber, protein, and authentic flavor.",
                "price": Decimal("190.00"),
                "discount_price": Decimal("165.00"),
                "stock": 50,
                "barcode": "8901052011018",
                "source_candidates": ["toor_dal.jpg"],
            },
            {
                "category": "pantry",
                "name": "Tata Pure Vacuum Evaporated Iodized Salt (1 kg)",
                "slug": "tata-pure-iodized-salt-1kg",
                "description": "Purity guaranteed vacuum-evaporated table salt containing optimal iodine for mental development.",
                "price": Decimal("28.00"),
                "discount_price": Decimal("24.00"),
                "stock": 85,
                "barcode": "8901030383701",
                "source_candidates": ["iodized_salt.jpg"],
            },

            # ==========================================
            # 8. HOME & PERSONAL CARE
            # ==========================================
            {
                "category": "home-care",
                "name": "Dettol Antiseptic Disinfectant Liquid (250 ml)",
                "slug": "dettol-antiseptic-liquid-250ml",
                "description": "Proven 99.9% germ protection for first aid, shaving, medical hygiene and surface sanitization.",
                "price": Decimal("142.00"),
                "discount_price": Decimal("128.00"),
                "stock": 60,
                "barcode": "8901396112104",
                "source_candidates": ["dettol_antiseptic_liquid_1789753520404.jpg"],
            },
            {
                "category": "home-care",
                "name": "Colgate MaxFresh Spicy Fresh Red Gel Toothpaste (150g)",
                "slug": "colgate-maxfresh-toothpaste-150g",
                "description": "Infused with cooling crystals that give an intense burst of spicy freshness and fight oral bacteria.",
                "price": Decimal("125.00"),
                "discount_price": Decimal("110.00"),
                "stock": 65,
                "barcode": "8901314010529",
                "source_candidates": ["colgate_maxfresh_1789753543365.jpg"],
            },
            {
                "category": "home-care",
                "name": "Surf Excel Quick Wash Detergent Powder (1 kg)",
                "slug": "surf-excel-quick-wash-powder-1kg",
                "description": "Premium detergent with stain-removing power that removes tough stains like oil, mud, and tea with ease.",
                "price": Decimal("180.00"),
                "discount_price": Decimal("155.00"),
                "stock": 55,
                "barcode": "8901030801014",
                "source_candidates": ["103678928_11.webp"],
            },
            {
                "category": "home-care",
                "name": "Ariel Complete Detergent Powder (4 kg Mega Pack)",
                "slug": "ariel-complete-detergent-powder-4kg",
                "description": "Deep clean technology that penetrates micro-fibers for bright, spotless whites and brilliant colored clothes.",
                "price": Decimal("499.00"),
                "discount_price": Decimal("425.00"),
                "stock": 40,
                "barcode": "8901030801015",
                "source_candidates": ["4-detergent-powder-complete-4kg-ariel-original-imafumtq2vbyqygm.webp"],
            },
            {
                "category": "home-care",
                "name": "Rin Advanced Detergent Powder (1 kg)",
                "slug": "rin-advanced-detergent-powder-1kg",
                "description": "Bright clothes that sparkle like new. Active formula removes deep-seated collar and cuff dirt.",
                "price": Decimal("90.00"),
                "discount_price": Decimal("75.00"),
                "stock": 50,
                "barcode": "8901030801016",
                "source_candidates": ["images_10_vUjaneo.jpg", "images_10.jpg"],
            },
            {
                "category": "home-care",
                "name": "Active Wheel 2-in-1 Detergent Powder (1 kg)",
                "slug": "wheel-2-in-1-clean-detergent-powder-1kg",
                "description": "With the power of lemons and thousands of flower extracts, gives fresh fragrance and clean wash.",
                "price": Decimal("50.00"),
                "discount_price": Decimal("42.00"),
                "stock": 60,
                "barcode": "8901030801017",
                "source_candidates": ["images_9_0Jzi49v.jpg", "images_9.jpg"],
            },
        ]

        # Valid slugs in our clean catalog
        valid_slugs = set()

        for pdata in products_data:
            cat = category_objs.get(pdata["category"])
            if not cat:
                continue

            slug = pdata["slug"]
            valid_slugs.add(slug)

            # Determine and prepare pure white background image
            clean_image_filename = f"{slug}.webp"
            clean_image_path = os.path.join(media_products_dir, clean_image_filename)

            source_file = find_source_image(pdata["source_candidates"])
            if source_file and (not os.path.exists(clean_image_path) or os.path.getsize(clean_image_path) < 2000):
                clean_to_pure_white_canvas(source_file, clean_image_path)

            # Final relative image path for Django ImageField
            if os.path.exists(clean_image_path):
                rel_img_path = f"products/{clean_image_filename}"
            elif source_file and source_file.startswith(settings.MEDIA_ROOT.as_posix()):
                rel_img_path = os.path.relpath(source_file, settings.MEDIA_ROOT).replace("\\", "/")
            elif source_file:
                # Copy directly if needed
                clean_to_pure_white_canvas(source_file, clean_image_path)
                rel_img_path = f"products/{clean_image_filename}"
            else:
                rel_img_path = f"products/{clean_image_filename}"

            barcode = pdata.get("barcode")
            if barcode:
                Product.objects.filter(barcode=barcode).exclude(slug=slug).update(barcode=None)

            defaults = {
                "category": cat,
                "name": pdata["name"],
                "description": pdata["description"],
                "price": pdata["price"],
                "discount_price": pdata["discount_price"],
                "stock": pdata["stock"],
                "available": True,
                "image": rel_img_path,
            }
            if barcode:
                defaults["barcode"] = barcode

            prod, created = Product.objects.update_or_create(
                slug=slug,
                defaults=defaults,
            )
            action = "Created" if created else "Updated"
            self.stdout.write(f"  [{cat.name}] {action}: {prod.name} (Rs. {prod.final_price})")

        # Clean up old random or duplicated test products that don't belong
        removed_count = 0
        for old_prod in Product.objects.exclude(slug__in=valid_slugs):
            self.stdout.write(f"  Removing outdated product: {old_prod.name} (slug={old_prod.slug})")
            old_prod.delete()
            removed_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSuccessfully seeded {len(valid_slugs)} products across 8 categories! Cleaned {removed_count} old items."
            )
        )
