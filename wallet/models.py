from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction


class Wallet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wallet"
    )
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00")
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wallet ({self.user.username}) - ₹{self.balance}"

    def credit(self, amount, description="Wallet Top-Up", reference_id=None):
        amount = Decimal(str(amount))
        if amount <= 0:
            raise ValidationError("Credit amount must be greater than zero.")

        with transaction.atomic():
            wallet_locked = Wallet.objects.select_for_update().get(id=self.id)
            wallet_locked.balance += amount
            wallet_locked.save()

            trx = WalletTransaction.objects.create(
                wallet=wallet_locked,
                transaction_type=WalletTransaction.CREDIT,
                amount=amount,
                balance_after=wallet_locked.balance,
                description=description,
                reference_id=reference_id
            )
            self.balance = wallet_locked.balance
            return trx

    def debit(self, amount, description="Order Payment", reference_id=None):
        amount = Decimal(str(amount))
        if amount <= 0:
            raise ValidationError("Debit amount must be greater than zero.")

        with transaction.atomic():
            wallet_locked = Wallet.objects.select_for_update().get(id=self.id)
            if wallet_locked.balance < amount:
                raise ValidationError("Insufficient wallet balance.")

            wallet_locked.balance -= amount
            wallet_locked.save()

            trx = WalletTransaction.objects.create(
                wallet=wallet_locked,
                transaction_type=WalletTransaction.DEBIT,
                amount=amount,
                balance_after=wallet_locked.balance,
                description=description,
                reference_id=reference_id
            )
            self.balance = wallet_locked.balance
            return trx

    def refund(self, amount, description="Order Cancellation Refund", reference_id=None):
        amount = Decimal(str(amount))
        if amount <= 0:
            raise ValidationError("Refund amount must be greater than zero.")

        with transaction.atomic():
            wallet_locked = Wallet.objects.select_for_update().get(id=self.id)
            wallet_locked.balance += amount
            wallet_locked.save()

            trx = WalletTransaction.objects.create(
                wallet=wallet_locked,
                transaction_type=WalletTransaction.REFUND,
                amount=amount,
                balance_after=wallet_locked.balance,
                description=description,
                reference_id=reference_id
            )
            self.balance = wallet_locked.balance
            return trx


class WalletTransaction(models.Model):
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"
    REFUND = "REFUND"

    TRANSACTION_TYPES = [
        (CREDIT, "Credit / Top-Up"),
        (DEBIT, "Debit / Payment"),
        (REFUND, "Refund"),
    ]

    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name="transactions"
    )
    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPES,
        default=CREDIT
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    balance_after = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    description = models.CharField(max_length=255)
    reference_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.transaction_type} of ₹{self.amount} ({self.wallet.user.username})"

