from django import forms
from .models import Voucher

class VoucherForm(forms.ModelForm):
    class Meta:
        model = Voucher
        fields = ['amount', 'product']

class RedeemVoucherForm(forms.Form):
    code = forms.CharField(max_length=12, label="Voucher Code")