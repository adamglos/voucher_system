from django import forms
from .models import Voucher

class VoucherForm(forms.ModelForm):
    quantity = forms.IntegerField(
        label="Ilość",
        min_value=1,
        max_value=10,
        initial=1,
        help_text="Wprowadź liczbę voucherów do wygenerowania (maks. 10)"
    )

    class Meta:
        model = Voucher
        fields = ['amount', 'product']  # Dodaj tutaj inne wymagane pola vouchera

class RedeemVoucherForm(forms.Form):
    code = forms.CharField(max_length=12, label="Voucher Code")