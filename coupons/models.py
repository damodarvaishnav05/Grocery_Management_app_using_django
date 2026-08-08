from django.db import models


class Coupon(models.Model):
    code = models.CharField(
        max_length=50,
        unique=True
    )

    discount_percent = models.PositiveIntegerField()

    minimum_order_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    active = models.BooleanField(default=True)

    valid_from = models.DateTimeField()

    valid_to = models.DateTimeField()

    usage_limit = models.PositiveIntegerField(default=100)

    used_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code