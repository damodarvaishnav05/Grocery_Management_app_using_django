from decimal import Decimal
from django import forms


class TopUpWalletForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("10.00"),
        max_value=Decimal("10000.00"),
        widget=forms.NumberInput(attrs={
            "class": "form-control form-control-lg rounded-pill px-4 fw-bold",
            "placeholder": "Enter amount (e.g. 500)",
            "min": "10",
            "max": "10000",
            "step": "1",
            "id": "topup-amount-input"
        })
    )

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount and amount < Decimal("10.00"):
            raise forms.ValidationError("Minimum top-up amount is ₹10.")
        if amount and amount > Decimal("10000.00"):
            raise forms.ValidationError("Maximum top-up amount at once is ₹10,000.")
        return amount

