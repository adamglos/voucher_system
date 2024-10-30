from django.utils import timezone
from django.shortcuts import render, redirect
from .forms import VoucherForm, RedeemVoucherForm
from .models import Voucher
import random
import string

def generate_voucher_code(length=8):
    letters_and_digits = string.ascii_uppercase + string.digits
    return ''.join(random.choice(letters_and_digits) for _ in range(length))

# vouchers/views.py
def create_voucher(request):
    error_message = None  # Przechowujemy ewentualny komunikat o błędzie

    if request.method == 'POST':
        form = VoucherForm(request.POST)
        if form.is_valid():
            voucher = form.save(commit=False)
            voucher.code = generate_voucher_code()
            voucher.save()
            qr_path = voucher.generate_qr_code()  # Generujemy kod QR

            if qr_path is None:
                # Ustawiamy komunikat błędu, jeśli zapis kodu QR się nie powiódł
                error_message = "Wystąpił problem przy generowaniu kodu QR."

            return redirect('voucher_created')
    else:
        form = VoucherForm()

    return render(request, 'create_voucher.html', {'form': form, 'error_message': error_message})

def redeem_voucher(request):
    message = None  # Przechowujemy komunikat błędu, jeśli voucher nie zostanie znaleziony lub jest już zrealizowany

    if request.method == 'POST':
        form = RedeemVoucherForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                # Pobieramy voucher, który nie został jeszcze wykorzystany
                voucher = Voucher.objects.get(code=code, is_redeemed=False)
                # Oznaczamy voucher jako zrealizowany
                voucher.is_redeemed = True
                voucher.redeemed_at = timezone.now()
                voucher.save()
                return render(request, 'voucher_redeemed.html', {'voucher': voucher})
            except Voucher.DoesNotExist:
                # Ustawiamy komunikat błędu, jeśli voucher nie istnieje lub jest już zrealizowany
                message = "Voucher o podanym kodzie nie istnieje lub został już wykorzystany."
    else:
        form = RedeemVoucherForm()

    return render(request, 'redeem_voucher.html', {'form': form, 'message': message})

def voucher_created(request):
    return render(request, 'voucher_created.html')

def recently_redeemed_vouchers(request):
    # Pobieramy 5 najnowszych wykorzystanych voucherów
    redeemed_vouchers = Voucher.objects.filter(is_redeemed=True).order_by('-redeemed_at')[:5]
    return render(request, 'recently_redeemed_vouchers.html', {'redeemed_vouchers': redeemed_vouchers})

def home(request):
    return render(request, 'home.html')