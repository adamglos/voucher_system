from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from .forms import VoucherForm, RedeemVoucherForm
from .models import Voucher
import random
import string
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm

def is_manager(user):
    return user.groups.filter(name='Managers').exists()

def generate_voucher_code(length=8):
    letters_and_digits = string.ascii_uppercase + string.digits
    return ''.join(random.choice(letters_and_digits) for _ in range(length))

@login_required
@user_passes_test(is_manager)
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

@login_required
def show_voucher(request):
    message = None

    if request.method == 'POST':
        form = RedeemVoucherForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                # Sprawdzenie, czy voucher istnieje i nie jest zrealizowany
                voucher = Voucher.objects.get(code=code, is_redeemed=False)

                # Przekierowanie do widoku szczegółów vouchera
                return redirect('voucher_details', code=code)

            except Voucher.DoesNotExist:
                message = "Voucher o podanym kodzie nie istnieje lub został już wykorzystany."
    else:
        form = RedeemVoucherForm()

    return render(request, 'show_voucher.html', {'form': form, 'message': message})

@login_required
@user_passes_test(is_manager)
def voucher_created(request):
    return render(request, 'voucher_created.html')

@login_required
def recently_redeemed_vouchers(request):
    # Pobieramy 5 najnowszych wykorzystanych voucherów
    redeemed_vouchers = Voucher.objects.filter(is_redeemed=True).order_by('-redeemed_at')[:5]
    return render(request, 'recently_redeemed_vouchers.html', {'redeemed_vouchers': redeemed_vouchers})

def home(request):
    is_manager = request.user.groups.filter(name='Managers').exists()

    context = {
        'is_manager': is_manager,
    }
    return render(request, 'home.html', context)

def voucher_details(request, code):
    # Pobieramy voucher na podstawie kodu, bez jego realizacji
    voucher = get_object_or_404(Voucher, code=code, is_redeemed=False)
    return render(request, 'voucher_details.html', {'voucher': voucher})

@login_required
def redeem_voucher(request, code):
    # Pobranie vouchera na podstawie kodu
    voucher = get_object_or_404(Voucher, code=code, is_redeemed=False)

    # Oznaczamy voucher jako zrealizowany
    voucher.is_redeemed = True
    voucher.redeemed_at = timezone.now()
    voucher.save()

    return render(request, 'voucher_redeemed.html', {'voucher': voucher})

def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()

    return render(request, 'custom_login.html', {'form': form})