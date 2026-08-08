from django.db import models
from products.models import Product


class InventoryHistory(models.Model):

    STOCK_IN = "STOCK_IN"
    STOCK_OUT = "STOCK_OUT"

    ACTIONS = (
        (STOCK_IN, "Stock In"),
        (STOCK_OUT, "Stock Out"),
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    action = models.CharField(
        max_length=20,
        choices=ACTIONS
    )

    quantity = models.PositiveIntegerField()

    note = models.CharField(
        max_length=255,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.product.name} - {self.action}"