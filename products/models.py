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

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def final_price(self):
        return self.discount_price if self.discount_price else self.price

    @property
    def average_rating(self):
        return self.reviews.aggregate(
            Avg("rating")
        )["rating__avg"] or 0


    @property
    def review_count(self):
        return self.reviews.count()