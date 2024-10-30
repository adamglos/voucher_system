from django.utils import timezone
from django.shortcuts import render, redirect
from .forms import VoucherForm, RedeemVoucherForm
from .models import Voucher
import random
import string

def generate_voucher_code(length=8):
    letters_and_digits = string.ascii_uppercase + string.digits
    return ''.join(random.choice(letters_and_digits) for _ in range(length))


def create_voucher(request):
    error_message = None

    if request.method == 'POST':
        form = VoucherForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            amount = form.cleaned_data['amount']
            product = form.cleaned_data['product']

            # Generowanie wielu voucherów
            for _ in range(quantity):
                voucher = Voucher(amount=amount, product=product, code=generate_voucher_code())
                voucher.save()
                voucher.generate_qr_code()

            return redirect('voucher_created')  # Przekierowanie do potwierdzenia po utworzeniu
    else:
        form = VoucherForm()

    return render(request, 'create_voucher.html', {'form': form, 'error_message': error_message})


def redeem_voucher(request):
    message = None
    voucher = None

    if request.method == 'POST':
        form = RedeemVoucherForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']

            try:
                # Pobieramy szczegóły vouchera bez oznaczania go jako zrealizowany
                voucher = Voucher.objects.get(code=code, is_redeemed=False)

                # Sprawdzamy, czy użytkownik kliknął przycisk "Zatwierdź realizację"
                if 'confirm_redeem' in request.POST:
                    voucher.is_redeemed = True
                    voucher.redeemed_at = timezone.now()
                    voucher.save()
                    return render(request, 'voucher_redeemed.html', {'voucher': voucher})

            except Voucher.DoesNotExist:
                message = "Voucher o podanym kodzie nie istnieje lub został już wykorzystany."
    else:
        form = RedeemVoucherForm()

    return render(request, 'redeem_voucher.html', {'form': form, 'voucher': voucher, 'message': message})

def voucher_created(request):
    return render(request, 'voucher_created.html')

def recently_redeemed_vouchers(request):
    # Pobieramy 5 najnowszych wykorzystanych voucherów
    redeemed_vouchers = Voucher.objects.filter(is_redeemed=True).order_by('-redeemed_at')[:5]
    return render(request, 'recently_redeemed_vouchers.html', {'redeemed_vouchers': redeemed_vouchers})

def home(request):
    return render(request, 'home.html')