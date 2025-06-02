from django import forms
from .models import Voucher
from django.contrib.auth.forms import AuthenticationForm

class VoucherForm(forms.ModelForm):
    class Meta:
        model = Voucher
        fields = ['amount', 'description']
        labels = {
            'amount': 'Kwota',
            'description': 'Krótki opis (max 50 znaków)'
        }
        widgets = {
            'description': forms.TextInput(attrs={'maxlength': 50}),
        }

class RedeemVoucherForm(forms.Form):
    code = forms.CharField(max_length=12, label="Kod vouchera")

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label="Nazwa użytkownika")
    password = forms.CharField(label="Hasło", widget=forms.PasswordInput)