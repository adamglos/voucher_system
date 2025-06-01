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
from .forms import CustomAuthenticationForm

def is_manager(user):
    return user.groups.filter(name='Managers').exists()

def is_shop(user):
    return user.groups.filter(name='Shops').exists()

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
    # Sprawdzamy, do jakiej grupy należy użytkownik
    is_manager_user = is_manager(request.user)
    is_shop_user = is_shop(request.user)

    # Filtrujemy vouchery w zależności od grupy użytkownika
    if is_manager_user:
        # Dla managerów pokazujemy wszystkie
        redeemed_vouchers = Voucher.objects.filter(is_redeemed=True).order_by('-redeemed_at')[:10]
    elif is_shop_user:
        # Dla sklepów pokazujemy tylko ich vouchery
        redeemed_vouchers = Voucher.objects.filter(
            is_redeemed=True, 
            redeemed_by=request.user
        ).order_by('-redeemed_at')[:10]
    else:
        # Dla innych użytkowników pusta lista (opcjonalnie)
        redeemed_vouchers = Voucher.objects.none()

    return render(request, 'recently_redeemed_vouchers.html', {
        'redeemed_vouchers': redeemed_vouchers,
        'is_manager': is_manager_user,
        'is_shop': is_shop_user
    })

@login_required
def home(request):
    is_manager_user = is_manager(request.user)
    is_shop_user = is_shop(request.user)

    context = {
        'is_manager': is_manager_user,
        'is_shop': is_shop_user
    }
    return render(request, 'home.html', context)

@login_required
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
    voucher.redeemed_by = request.user
    voucher.save()

    return render(request, 'voucher_redeemed.html', {'voucher': voucher})

def custom_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = CustomAuthenticationForm()

    return render(request, 'custom_login.html', {'form': form})