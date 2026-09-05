from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager


class CustomUser(AbstractUser):

    CUSTOMER = "CUSTOMER"
    ADMIN = "ADMIN"

    ROLE_CHOICES = (
        (CUSTOMER, "Customer"),
        (ADMIN, "Admin"),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=CUSTOMER
    )

    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    profile_picture = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True
    )

    is_email_verified = models.BooleanField(
        default=False
    )

    referral_code = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        db_index=True
    )

    referred_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="referrals"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    objects = CustomUserManager()

    def generate_unique_referral_code(self):
        import secrets
        import string
        characters = string.ascii_uppercase + string.digits.replace("0", "").replace("O", "")
        while True:
            code = "OM" + "".join(secrets.choice(characters) for _ in range(6))
            if not CustomUser.objects.filter(referral_code=code).exists():
                return code

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = self.generate_unique_referral_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username