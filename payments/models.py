from django.db import models
from orders.models import Order


class Payment(models.Model):

    PENDING = "Pending"
    SUCCESS = "Success"
    FAILED = "Failed"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (SUCCESS, "Success"),
        (FAILED, "Failed"),
    ]

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="payment"
    )

    razorpay_order_id = models.CharField(
        max_length=200,
        blank=True
    )

    razorpay_payment_id = models.CharField(
        max_length=200,
        blank=True
    )

    razorpay_signature = models.CharField(
        max_length=300,
        blank=True
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Order #{self.order.id}"