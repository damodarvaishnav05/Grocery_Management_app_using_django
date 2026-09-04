from decimal import Decimal
import os
from django.core.management.base import BaseCommand
from categories.models import Category
from products.models import Product


class Command(BaseCommand):
    help = "Seeds comprehensive grocery categories and products with images and stock"

    def handle(self, *args, **options):
        self.stdout.write("Seeding categories and products...")

        categories_data = [
            {
                "name": "Fresh Fruits",
                "slug": "fruits",
                "icon": "bi-apple",
                "description": "Farm-fresh fruits picked daily for maximum sweetness and nutrition.",
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
            cat, created = Category.objects.update_or_create(
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
            status = "Created" if created else "Updated"
            self.stdout.write(f"  {status} category: {cat.name}")

        products_data = [
            # Fresh Fruits
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
                "description": "Naturally ripened Robusta bananas packed with potassium and instant natural energy. Ideal for morning breakfast.",
                "price": Decimal("65.00"),
                "discount_price": Decimal("48.00"),
                "stock": 60,
                "image": "products/images_1.jpg",
            },
            {
                "category": "fruits",
                "name": "Alphonso Mangoes (Box of 6)",
                "slug": "alphonso-mangoes-box-6",
                "description": "The king of mangoes. Hand-harvested from Ratnagiri farms, golden pulped, and heavenly sweet.",
                "price": Decimal("499.00"),
                "discount_price": Decimal("399.00"),
                "stock": 25,
                "image": "products/images_2.jpg",
            },
            {
                "category": "fruits",
                "name": "Ruby Red Pomegranate (1 kg)",
                "slug": "ruby-red-pomegranate-1kg",
                "description": "Juicy, ruby-red arils rich in vitamin C and polyphenols. Promotes heart health and radiant skin.",
                "price": Decimal("220.00"),
                "discount_price": Decimal("185.00"),
                "stock": 35,
                "image": "products/images_3.jpg",
            },
            {
                "category": "fruits",
                "name": "Nagpur Sweet Oranges (1 kg)",
                "slug": "nagpur-sweet-oranges-1kg",
                "description": "Juicy Nagpur oranges with the perfect balance of sweet and tangy citrus flavors. High in vitamin C.",
                "price": Decimal("110.00"),
                "discount_price": Decimal("89.00"),
                "stock": 40,
                "image": "products/images_4.jpg",
            },

            # Fresh Vegetables
            {
                "category": "vegetables",
                "name": "Farm Fresh Potatoes (2 kg)",
                "slug": "farm-fresh-potatoes-2kg",
                "description": "Unpolished, earthy farm potatoes suitable for baking, boiling, fries, and everyday curries.",
                "price": Decimal("70.00"),
                "discount_price": Decimal("54.00"),
                "stock": 80,
                "image": "products/images_5.jpg",
            },
            {
                "category": "vegetables",
                "name": "Fresh Red Onions (2 kg)",
                "slug": "fresh-red-onions-2kg",
                "description": "Pungent, crisp and flavorful red onions essential for every kitchen base and fresh salads.",
                "price": Decimal("80.00"),
                "discount_price": Decimal("65.00"),
                "stock": 90,
                "image": "products/images_7.jpg",
            },
            {
                "category": "vegetables",
                "name": "Vine Ripe Hybrid Tomatoes (1 kg)",
                "slug": "vine-ripe-hybrid-tomatoes-1kg",
                "description": "Juicy, firm, deep red tomatoes harvested at peak ripeness. Perfect for sauces and salads.",
                "price": Decimal("50.00"),
                "discount_price": Decimal("38.00"),
                "stock": 70,
                "image": "products/images_9.jpg",
            },
            {
                "category": "vegetables",
                "name": "Fresh Baby Spinach / Palak (250g)",
                "slug": "fresh-baby-spinach-250g",
                "description": "Tender hydroponic baby spinach leaves, hydro-cooled and cleaned. Rich in iron and folate.",
                "price": Decimal("35.00"),
                "discount_price": Decimal("26.00"),
                "stock": 30,
                "image": "products/images_10.jpg",
            },
            {
                "category": "vegetables",
                "name": "Crunchy English Cucumbers (500g)",
                "slug": "crunchy-english-cucumbers-500g",
                "description": "Seedless, crisp and refreshing cucumbers. 96% water content for effortless hydration.",
                "price": Decimal("40.00"),
                "discount_price": Decimal("29.00"),
                "stock": 50,
                "image": "products/images.jpg",
            },

            # Dairy, Bread & Eggs
            {
                "category": "dairy-bread-eggs",
                "name": "Fresh Cow Milk - Full Cream (1 Litre)",
                "slug": "fresh-cow-milk-1-litre",
                "description": "Pure, pasteurized farm fresh cow milk with rich natural cream. Delivered cold within hours of milking.",
                "price": Decimal("72.00"),
                "discount_price": Decimal("66.00"),
                "stock": 50,
                "image": "products/103678928_11.webp",
            },
            {
                "category": "dairy-bread-eggs",
                "name": "Farm Fresh White Eggs (Pack of 12)",
                "slug": "farm-fresh-white-eggs-12pk",
                "description": "Grade-A farm eggs, cleaned and tested. Packed with 6g of high-biological value protein per egg.",
                "price": Decimal("105.00"),
                "discount_price": Decimal("88.00"),
                "stock": 40,
                "image": "products/images_3_ul3C26A.jpg",
            },
            {
                "category": "dairy-bread-eggs",
                "name": "Fresh Malai Paneer (200g)",
                "slug": "fresh-malai-paneer-200g",
                "description": "Melt-in-the-mouth soft cottage cheese made from 100% cow milk. Unmatched freshness for your curries.",
                "price": Decimal("115.00"),
                "discount_price": Decimal("99.00"),
                "stock": 35,
                "image": "products/images_4_DFLE0QW.jpg",
            },
            {
                "category": "dairy-bread-eggs",
                "name": "100% Whole Wheat Bread (400g)",
                "slug": "100-percent-whole-wheat-bread-400g",
                "description": "Zero maida, high-fiber whole grain loaf baked fresh each dawn. Toasts to a golden, nutty perfection.",
                "price": Decimal("55.00"),
                "discount_price": Decimal("48.00"),
                "stock": 30,
                "image": "products/images_5_L7fwxu4.jpg",
            },

            # Beverages & Juices
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
                "image": "products/images_4_hV97jQO.jpg",
            },
            {
                "category": "beverages",
                "name": "Natural Tender Coconut Water (Pack of 2)",
                "slug": "natural-tender-coconut-water-2pk",
                "description": "Naturally electrolyte-rich fresh coconut water. Restores hydration instantly after workouts.",
                "price": Decimal("120.00"),
                "discount_price": Decimal("99.00"),
                "stock": 30,
                "image": "products/images_10_vUjaneo.jpg",
            },

            # Bakery & Cakes
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
                "image": "products/images_5_qAWhPkg.jpg",
            },

            # Home & Personal Care
            {
                "category": "home-care",
                "name": "Ariel Complete Detergent Powder (4 kg)",
                "slug": "ariel-complete-detergent-powder-4kg",
                "description": "Deep stain removal in just 1 wash with freshness technology. Safe for whites and colors in top/front load.",
                "price": Decimal("499.00"),
                "discount_price": Decimal("425.00"),
                "stock": 40,
                "image": "products/4-detergent-powder-complete-4kg-ariel-original-imafumtq2vbyqygm.webp",
            },

            # Pantry Staples
            {
                "category": "pantry",
                "name": "Daawat Rozana Super Basmati Rice (1 kg)",
                "slug": "daawat-rozana-super-basmati-rice-1kg",
                "description": "Aromatic, extra-long slender grains aged to perfection. Fluffy, non-sticky and royal aroma.",
                "price": Decimal("165.00"),
                "discount_price": Decimal("139.00"),
                "stock": 60,
                "image": "products/images_9_0Jzi49v.jpg",
            },
            {
                "category": "pantry",
                "name": "Organic Unpolished Toor Dal (1 kg)",
                "slug": "organic-unpolished-toor-dal-1kg",
                "description": "Pesticide-free yellow pigeon peas unpolished to retain 100% natural fiber, protein, and flavor.",
                "price": Decimal("190.00"),
                "discount_price": Decimal("165.00"),
                "stock": 50,
                "image": "products/images_3.jpg",
            },

            # Snacks
            {
                "category": "snacks",
                "name": "California Roasted & Salted Almonds (250g)",
                "slug": "california-roasted-salted-almonds-250g",
                "description": "Crunchy whole California almonds slow-roasted and lightly sprinkled with Himalayan pink salt.",
                "price": Decimal("320.00"),
                "discount_price": Decimal("269.00"),
                "stock": 35,
                "image": "products/images_2.jpg",
            },
            {
                "category": "snacks",
                "name": "All-Natural Crunchy Peanut Butter (350g)",
                "slug": "all-natural-crunchy-peanut-butter-350g",
                "description": "100% roasted peanuts with crunchy bits. Zero hydrogenated oils, zero refined sugar. 30% natural protein.",
                "price": Decimal("195.00"),
                "discount_price": Decimal("165.00"),
                "stock": 40,
                "image": "products/images_7.jpg",
            },
        ]

        for pdata in products_data:
            cat = category_objs.get(pdata["category"])
            if not cat:
                continue

            prod, created = Product.objects.update_or_create(
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
            status = "Created" if created else "Updated"
            self.stdout.write(f"  {status} product: {prod.name} (Rs. {prod.final_price})")

        self.stdout.write(self.style.SUCCESS("Successfully seeded categories and products!"))
