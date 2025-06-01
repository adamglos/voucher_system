from django import forms
from .models import Voucher
from django.contrib.auth.forms import AuthenticationForm

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
        labels = {
            'amount': 'Kwota',
            'product': 'Produkt',
        }

class RedeemVoucherForm(forms.Form):
    code = forms.CharField(max_length=12, label="Kod Vouchera")

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label="Nazwa użytkownika")
    password = forms.CharField(label="Hasło", widget=forms.PasswordInput)