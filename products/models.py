from django.db import models
from categories.models import Category
from django.db.models import Avg


class Product(models.Model):

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products"
    )

    name = models.CharField(max_length=200)

    slug = models.SlugField(unique=True)

    description = models.TextField()

    image = models.ImageField(
        upload_to="products/"
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    stock = models.PositiveIntegerField(default=0)

    available = models.BooleanField(default=True)

    barcode = models.CharField(
        max_length=64,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        help_text="UPC, EAN-13, or custom product barcode"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.barcode:
            # Auto-generate unique 13-digit EAN-style barcode based on product ID
            self.barcode = f"890103{self.id:07d}"
            Product.objects.filter(pk=self.pk).update(barcode=self.barcode)

    def __str__(self):
        return self.name

    @property
    def final_price(self):
        return self.discount_price if self.discount_price else self.price

    @property
    def discount_percent(self):
        if self.discount_price and self.price > self.discount_price and self.price > 0:
            return int(round(((self.price - self.discount_price) / self.price) * 100))
        return 0

    @property
    def savings_amount(self):
        if self.discount_price and self.price > self.discount_price:
            return self.price - self.discount_price
        return 0

    @property
    def average_rating(self):
        return self.reviews.aggregate(
            Avg("rating")
        )["rating__avg"] or 0

    @property
    def review_count(self):
        return self.reviews.count()