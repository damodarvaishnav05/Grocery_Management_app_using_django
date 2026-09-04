from django.contrib import admin
from .models import Wallet, WalletTransaction


class WalletTransactionInline(admin.TabularInline):
    model = WalletTransaction
    extra = 0
    readonly_fields = [
        "transaction_type",
        "amount",
        "balance_after",
        "description",
        "reference_id",
        "created_at",
    ]
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "balance",
        "is_active",
        "updated_at",
        "created_at",
    ]
    list_filter = ["is_active", "updated_at"]
    search_fields = ["user__username", "user__email"]
    readonly_fields = ["created_at", "updated_at"]
    inlines = [WalletTransactionInline]


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = [
        "wallet",
        "transaction_type",
        "amount",
        "balance_after",
        "description",
        "reference_id",
        "created_at",
    ]
    list_filter = ["transaction_type", "created_at"]
    search_fields = [
        "wallet__user__username",
        "wallet__user__email",
        "description",
        "reference_id",
    ]
    readonly_fields = [
        "wallet",
        "transaction_type",
        "amount",
        "balance_after",
        "description",
        "reference_id",
        "created_at",
    ]

