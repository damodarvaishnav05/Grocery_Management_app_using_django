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
        default="FreshMart Express Hub #4 - Baner"
    )

    dark_store_address = models.CharField(
        max_length=255,
        default="Plot 12, Baner High Street, Pune, Maharashtra 411045"
    )

    # Coordinates
    dark_store_lat = models.FloatField(default=18.5590)
    dark_store_lng = models.FloatField(default=73.7868)
    customer_lat = models.FloatField(default=18.5685)
    customer_lng = models.FloatField(default=73.7745)

    # Courier partner info
    rider_name = models.CharField(max_length=100, default="Vikram Shinde")
    rider_phone = models.CharField(max_length=20, default="+91 98230 45678")
    rider_vehicle = models.CharField(max_length=100, default="Ather 450X Electric (MH-12-BF-4892)")
    rider_rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.9)
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
        tracking, _ = cls.objects.get_or_create(
            order=order,
            defaults={
                "dark_store_name": "FreshMart Express Hub #4 - Baner",
                "dark_store_address": "Plot 12, Baner High Street, Pune, Maharashtra 411045",
                "dark_store_lat": 18.5590,
                "dark_store_lng": 73.7868,
                "customer_lat": 18.5685,
                "customer_lng": 73.7745,
                "rider_name": "Vikram Shinde",
                "rider_phone": "+91 98230 45678",
                "rider_vehicle": "Ather 450X Electric (MH-12-BF-4892)",
                "rider_rating": 4.9,
                "delivery_pin": str(1000 + (order.id * 137) % 9000),
            }
        )
        return tracking

    def get_live_telemetry(self):
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
            }

        # Check manual override
        if self.override_stage:
            stage = self.override_stage
            if stage == self.STAGE_DELIVERED:
                return {
                    "stage": self.STAGE_DELIVERED,
                    "stage_title": "Order Delivered Successfully!",
                    "stage_desc": "Delivered to your doorstep. Thank you for shopping fresh at FreshMart!",
                    "progress": 100,
                    "eta_minutes": 0,
                    "rider_lat": self.customer_lat,
                    "rider_lng": self.customer_lng,
                    "is_delivered": True,
                    "is_cancelled": False,
                }
            elif stage == self.STAGE_RECEIVED:
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
                }
            elif stage == self.STAGE_ON_THE_WAY:
                rider_lat = self.dark_store_lat + 0.60 * (self.customer_lat - self.dark_store_lat)
                rider_lng = self.dark_store_lng + 0.60 * (self.customer_lng - self.dark_store_lng)
                return {
                    "stage": self.STAGE_ON_THE_WAY,
                    "stage_title": "Rider On The Way! 🛵",
                    "stage_desc": f"{self.rider_name} is riding to your location with your fresh items.",
                    "progress": 70,
                    "eta_minutes": 4,
                    "rider_lat": round(rider_lat, 6),
                    "rider_lng": round(rider_lng, 6),
                    "is_delivered": False,
                    "is_cancelled": False,
                }
            elif stage == self.STAGE_ARRIVING:
                rider_lat = self.dark_store_lat + 0.94 * (self.customer_lat - self.dark_store_lat)
                rider_lng = self.dark_store_lng + 0.94 * (self.customer_lng - self.dark_store_lng)
                return {
                    "stage": self.STAGE_ARRIVING,
                    "stage_title": "Arriving at Your Gate / Doorstep!",
                    "stage_desc": f"Rider is right outside. Share Delivery PIN {self.delivery_pin} to collect your order.",
                    "progress": 94,
                    "eta_minutes": 1,
                    "rider_lat": round(rider_lat, 6),
                    "rider_lng": round(rider_lng, 6),
                    "is_delivered": False,
                    "is_cancelled": False,
                }

        # Otherwise calculate from elapsed real time
        from django.utils import timezone
        elapsed = (timezone.now() - self.order.created_at).total_seconds()

        if self.order.status == Order.DELIVERED or elapsed >= 720:
            return {
                "stage": self.STAGE_DELIVERED,
                "stage_title": "Order Delivered Successfully!",
                "stage_desc": "Delivered to your doorstep. Thank you for shopping fresh at FreshMart!",
                "progress": 100,
                "eta_minutes": 0,
                "rider_lat": self.customer_lat,
                "rider_lng": self.customer_lng,
                "is_delivered": True,
                "is_cancelled": False,
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
            }
        elif elapsed < 600:
            fraction = (elapsed - 270) / (600 - 270)
            rider_lat = self.dark_store_lat + fraction * (self.customer_lat - self.dark_store_lat)
            rider_lng = self.dark_store_lng + fraction * (self.customer_lng - self.dark_store_lng)
            eta = max(2, int(11 - (elapsed / 60)))
            return {
                "stage": self.STAGE_ON_THE_WAY,
                "stage_title": "Rider On The Way! 🛵",
                "stage_desc": f"{self.rider_name} is riding along the express delivery corridor.",
                "progress": int(45 + fraction * 45),
                "eta_minutes": eta,
                "rider_lat": round(rider_lat, 6),
                "rider_lng": round(rider_lng, 6),
                "is_delivered": False,
                "is_cancelled": False,
            }
        else:
            rider_lat = self.dark_store_lat + 0.94 * (self.customer_lat - self.dark_store_lat)
            rider_lng = self.dark_store_lng + 0.94 * (self.customer_lng - self.dark_store_lng)
            return {
                "stage": self.STAGE_ARRIVING,
                "stage_title": "Arriving at Your Gate / Doorstep!",
                "stage_desc": f"Rider is right outside. Share Delivery PIN {self.delivery_pin} to collect your order.",
                "progress": 95,
                "eta_minutes": 1,
                "rider_lat": round(rider_lat, 6),
                "rider_lng": round(rider_lng, 6),
                "is_delivered": False,
                "is_cancelled": False,
            }

    def __str__(self):
        return f"Tracking for Order #{self.order_id} ({self.rider_name})"