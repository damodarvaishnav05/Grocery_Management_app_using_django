from django.db import models
from django.conf import settings
from products.models import Product


class Order(models.Model):

    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    SHIPPED = "Shipped"
    DELIVERED = "Delivered"
    CANCELLED = "Cancelled"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (CONFIRMED, "Confirmed"),
        (SHIPPED, "Shipped"),
        (DELIVERED, "Delivered"),
        (CANCELLED, "Cancelled"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    full_name = models.CharField(max_length=100)

    phone = models.CharField(max_length=20)

    address = models.TextField()

    city = models.CharField(max_length=100)

    state = models.CharField(max_length=100)

    pincode = models.CharField(max_length=10)

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def get_tracking(self):
        return OrderDeliveryTracking.get_or_create_for_order(self)

    def __str__(self):
        return f"Order #{self.id}"


class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def subtotal(self):
        return self.quantity * self.price

    def __str__(self):
        return self.product.name


class OrderDeliveryTracking(models.Model):

    STAGE_RECEIVED = "RECEIVED"
    STAGE_PACKED = "PACKED"
    STAGE_ON_THE_WAY = "ON_THE_WAY"
    STAGE_ARRIVING = "ARRIVING"
    STAGE_DELIVERED = "DELIVERED"
    STAGE_CANCELLED = "CANCELLED"

    STAGE_CHOICES = [
        (STAGE_RECEIVED, "Order Confirmed & Received"),
        (STAGE_PACKED, "Packed at Micro-Hub"),
        (STAGE_ON_THE_WAY, "Rider On The Way"),
        (STAGE_ARRIVING, "Arriving at Doorstep"),
        (STAGE_DELIVERED, "Delivered"),
        (STAGE_CANCELLED, "Cancelled"),
    ]

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="tracking"
    )

    dark_store_name = models.CharField(
        max_length=150,
        default="Om Super Mart Express Hub #4 - Indore"
    )

    dark_store_address = models.CharField(
        max_length=255,
        default="Plot 12, Main Ring Road, Indore, Madhya Pradesh 452001"
    )

    # Coordinates
    dark_store_lat = models.FloatField(default=22.7196)
    dark_store_lng = models.FloatField(default=75.8577)
    customer_lat = models.FloatField(default=22.7290)
    customer_lng = models.FloatField(default=75.8650)

    # Real-time Rider GPS Coordinates & Live Tracking status
    rider_lat = models.FloatField(null=True, blank=True)
    rider_lng = models.FloatField(null=True, blank=True)
    is_live_tracking_active = models.BooleanField(default=False)
    partner_access_token = models.CharField(max_length=64, blank=True, default="")

    # Courier partner info (Real Verified Delivery Partner)
    rider_name = models.CharField(max_length=100, default="Damodar Vaishnav")
    rider_phone = models.CharField(max_length=20, default="+91 90220 54562")
    rider_vehicle = models.CharField(max_length=100, default="Electric Delivery Scooter (MP-09)")
    rider_rating = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)
    delivery_pin = models.CharField(max_length=6, default="4821")

    # Manual stage override for testing or simulator
    override_stage = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        choices=STAGE_CHOICES,
        help_text="Manual override for testing simulator stages"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_or_create_for_order(cls, order):
        import secrets

        city_coords = {
            "indore": (22.7196, 75.8577),
            "bhopal": (23.2599, 77.4126),
            "mumbai": (19.0760, 72.8777),
            "pune": (18.5204, 73.8567),
            "delhi": (28.6139, 77.2090),
            "bengaluru": (12.9716, 77.5946),
            "bangalore": (12.9716, 77.5946),
            "jaipur": (26.9124, 75.7873),
            "hyderabad": (17.3850, 78.4867),
            "ahmedabad": (23.0225, 72.5714),
            "nagpur": (21.1458, 79.0882),
        }
        order_city = (order.city or "").strip().lower()
        base_lat, base_lng = city_coords.get(order_city, (22.7196, 75.8577))
        city_display = (order.city or "Indore").strip().title()

        tracking, created = cls.objects.get_or_create(
            order=order,
            defaults={
                "dark_store_name": f"Om Super Mart Express Hub - {city_display}",
                "dark_store_address": f"Express Micro-Fulfillment Center, {city_display}",
                "dark_store_lat": base_lat,
                "dark_store_lng": base_lng,
                "customer_lat": round(base_lat + 0.0115, 6),
                "customer_lng": round(base_lng + 0.0085, 6),
                "rider_name": "Damodar Vaishnav",
                "rider_phone": "+91 90220 54562",
                "rider_vehicle": "Electric Delivery Scooter (MP-09)",
                "rider_rating": 5.0,
                "delivery_pin": str(1000 + (order.id * 137) % 9000),
                "partner_access_token": secrets.token_hex(16),
            }
        )

        changed = False
        if not tracking.partner_access_token:
            tracking.partner_access_token = secrets.token_hex(16)
            changed = True
        if tracking.rider_name in ("Vikram Shinde", ""):
            tracking.rider_name = "Damodar Vaishnav"
            tracking.rider_phone = "+91 90220 54562"
            tracking.rider_vehicle = "Electric Delivery Scooter (MP-09)"
            tracking.rider_rating = 5.0
            changed = True
        if changed:
            tracking.save()

        return tracking

    def get_live_telemetry(self):
        import math
        from django.utils import timezone

        if self.order.status == Order.CANCELLED or self.override_stage == self.STAGE_CANCELLED:
            return {
                "stage": self.STAGE_CANCELLED,
                "stage_title": "Order Cancelled",
                "stage_desc": "This order was cancelled. Any amount paid has been refunded to your FreshCash wallet.",
                "progress": 0,
                "eta_minutes": 0,
                "rider_lat": self.dark_store_lat,
                "rider_lng": self.dark_store_lng,
                "is_delivered": False,
                "is_cancelled": True,
                "is_live_gps": False,
            }

        if self.order.status == Order.DELIVERED or self.override_stage == self.STAGE_DELIVERED:
            return {
                "stage": self.STAGE_DELIVERED,
                "stage_title": "Order Delivered Successfully! 🎉",
                "stage_desc": "Delivered to your doorstep. Thank you for shopping fresh at Om Super Mart!",
                "progress": 100,
                "eta_minutes": 0,
                "rider_lat": self.customer_lat,
                "rider_lng": self.customer_lng,
                "is_delivered": True,
                "is_cancelled": False,
                "is_live_gps": bool(self.is_live_tracking_active),
            }

        # If live GPS tracking is active from partner portal
        if self.is_live_tracking_active and self.rider_lat is not None and self.rider_lng is not None:
            R = 6371.0
            dlat = math.radians(self.customer_lat - self.rider_lat)
            dlng = math.radians(self.customer_lng - self.rider_lng)
            a = math.sin(dlat / 2)**2 + math.cos(math.radians(self.rider_lat)) * math.cos(math.radians(self.customer_lat)) * math.sin(dlng / 2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            dist_km = R * c

            eta = max(1, int(math.ceil(dist_km * 2.8)))

            if self.override_stage:
                stage = self.override_stage
            elif dist_km < 0.20:
                stage = self.STAGE_ARRIVING
            else:
                stage = self.STAGE_ON_THE_WAY

            if stage == self.STAGE_ARRIVING:
                stage_title = "Arriving at Your Gate / Doorstep!"
                stage_desc = f"{self.rider_name} is right outside. Share Delivery PIN {self.delivery_pin} to collect your order."
                progress = 95
            else:
                stage_title = f"{self.rider_name} is on the way! 🛵"
                stage_desc = f"Live GPS active • Approx {dist_km:.1f} km away from your delivery address."
                progress = max(50, min(92, int(100 - dist_km * 20)))

            return {
                "stage": stage,
                "stage_title": stage_title,
                "stage_desc": stage_desc,
                "progress": progress,
                "eta_minutes": eta,
                "rider_lat": round(self.rider_lat, 6),
                "rider_lng": round(self.rider_lng, 6),
                "is_delivered": False,
                "is_cancelled": False,
                "is_live_gps": True,
                "distance_km": round(dist_km, 2),
            }

        # Check manual override stage when live GPS not active
        if self.override_stage:
            stage = self.override_stage
            if stage == self.STAGE_RECEIVED:
                return {
                    "stage": self.STAGE_RECEIVED,
                    "stage_title": "Order Confirmed & Received",
                    "stage_desc": f"Received at {self.dark_store_name}. Dedicated picker is assembling your items.",
                    "progress": 20,
                    "eta_minutes": 11,
                    "rider_lat": self.dark_store_lat,
                    "rider_lng": self.dark_store_lng,
                    "is_delivered": False,
                    "is_cancelled": False,
                    "is_live_gps": False,
                }
            elif stage == self.STAGE_PACKED:
                return {
                    "stage": self.STAGE_PACKED,
                    "stage_title": "Quality Checked & Packed",
                    "stage_desc": f"Groceries packed in sanitized thermal bags. Handed over to {self.rider_name}.",
                    "progress": 45,
                    "eta_minutes": 8,
                    "rider_lat": self.dark_store_lat,
                    "rider_lng": self.dark_store_lng,
                    "is_delivered": False,
                    "is_cancelled": False,
                    "is_live_gps": False,
                }
            elif stage == self.STAGE_ON_THE_WAY:
                rider_lat = self.dark_store_lat + 0.60 * (self.customer_lat - self.dark_store_lat)
                rider_lng = self.dark_store_lng + 0.60 * (self.customer_lng - self.dark_store_lng)
                return {
                    "stage": self.STAGE_ON_THE_WAY,
                    "stage_title": f"{self.rider_name} On The Way! 🛵",
                    "stage_desc": f"{self.rider_name} is riding to your location with your fresh items.",
                    "progress": 70,
                    "eta_minutes": 4,
                    "rider_lat": round(rider_lat, 6),
                    "rider_lng": round(rider_lng, 6),
                    "is_delivered": False,
                    "is_cancelled": False,
                    "is_live_gps": False,
                }
            elif stage == self.STAGE_ARRIVING:
                rider_lat = self.dark_store_lat + 0.94 * (self.customer_lat - self.dark_store_lat)
                rider_lng = self.dark_store_lng + 0.94 * (self.customer_lng - self.dark_store_lng)
                return {
                    "stage": self.STAGE_ARRIVING,
                    "stage_title": "Arriving at Your Gate / Doorstep!",
                    "stage_desc": f"{self.rider_name} is right outside. Share Delivery PIN {self.delivery_pin} to collect your order.",
                    "progress": 94,
                    "eta_minutes": 1,
                    "rider_lat": round(rider_lat, 6),
                    "rider_lng": round(rider_lng, 6),
                    "is_delivered": False,
                    "is_cancelled": False,
                    "is_live_gps": False,
                }

        # Otherwise calculate from elapsed real time
        elapsed = (timezone.now() - self.order.created_at).total_seconds()

        if elapsed >= 720:
            return {
                "stage": self.STAGE_DELIVERED,
                "stage_title": "Order Delivered Successfully!",
                "stage_desc": "Delivered to your doorstep. Thank you for shopping fresh at Om Super Mart!",
                "progress": 100,
                "eta_minutes": 0,
                "rider_lat": self.customer_lat,
                "rider_lng": self.customer_lng,
                "is_delivered": True,
                "is_cancelled": False,
                "is_live_gps": False,
            }
        elif elapsed < 120:
            return {
                "stage": self.STAGE_RECEIVED,
                "stage_title": "Order Confirmed & Received",
                "stage_desc": f"Received at {self.dark_store_name}. Dedicated picker is assembling your items.",
                "progress": 20,
                "eta_minutes": 11,
                "rider_lat": self.dark_store_lat,
                "rider_lng": self.dark_store_lng,
                "is_delivered": False,
                "is_cancelled": False,
                "is_live_gps": False,
            }
        elif elapsed < 270:
            return {
                "stage": self.STAGE_PACKED,
                "stage_title": "Quality Checked & Packed",
                "stage_desc": f"Groceries packed in sanitized bags. Handed over to {self.rider_name}.",
                "progress": 45,
                "eta_minutes": 8,
                "rider_lat": self.dark_store_lat,
                "rider_lng": self.dark_store_lng,
                "is_delivered": False,
                "is_cancelled": False,
                "is_live_gps": False,
            }
        elif elapsed < 600:
            fraction = (elapsed - 270) / (600 - 270)
            rider_lat = self.dark_store_lat + fraction * (self.customer_lat - self.dark_store_lat)
            rider_lng = self.dark_store_lng + fraction * (self.customer_lng - self.dark_store_lng)
            eta = max(2, int(11 - (elapsed / 60)))
            return {
                "stage": self.STAGE_ON_THE_WAY,
                "stage_title": f"{self.rider_name} On The Way! 🛵",
                "stage_desc": f"{self.rider_name} is riding along the express delivery corridor.",
                "progress": int(45 + fraction * 45),
                "eta_minutes": eta,
                "rider_lat": round(rider_lat, 6),
                "rider_lng": round(rider_lng, 6),
                "is_delivered": False,
                "is_cancelled": False,
                "is_live_gps": False,
            }
        else:
            rider_lat = self.dark_store_lat + 0.94 * (self.customer_lat - self.dark_store_lat)
            rider_lng = self.dark_store_lng + 0.94 * (self.customer_lng - self.dark_store_lng)
            return {
                "stage": self.STAGE_ARRIVING,
                "stage_title": "Arriving at Your Gate / Doorstep!",
                "stage_desc": f"{self.rider_name} is right outside. Share Delivery PIN {self.delivery_pin} to collect your order.",
                "progress": 95,
                "eta_minutes": 1,
                "rider_lat": round(rider_lat, 6),
                "rider_lng": round(rider_lng, 6),
                "is_delivered": False,
                "is_cancelled": False,
                "is_live_gps": False,
            }

    def __str__(self):
        return f"Tracking for Order #{self.order_id} ({self.rider_name})"