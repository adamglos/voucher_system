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
from django.core.paginator import Paginator

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
            amount = form.cleaned_data['amount']
            description = form.cleaned_data['description']

            # Generowanie pojedynczego vouchera
            voucher = Voucher(
                amount=amount, 
                description=description,
                code=generate_voucher_code(),
                created_by=request.user
            )
            voucher.save()
            voucher.generate_qr_code()

            # Przekierowanie do podsumowania z wygenerowanym voucherem
            return redirect('voucher_created', code=voucher.code)
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
                # Przekierowanie do nowej strony z informacją o błędzie
                return render(request, 'voucher_not_found.html', {
                    'message': 'Voucher o podanym kodzie nie istnieje lub został już wykorzystany.'
                })
    else:
        form = RedeemVoucherForm()

    return render(request, 'show_voucher.html', {'form': form, 'message': message})

@login_required
@user_passes_test(is_manager)
def voucher_created(request, code):
    # Pobieramy utworzony voucher na podstawie kodu
    voucher = get_object_or_404(Voucher, code=code)
    return render(request, 'voucher_created.html', {'voucher': voucher})

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
    # Strona główna aplikacji - sprawdzamy uprawnienia użytkownika, aby wyświetlić odpowiednie przyciski
    is_manager_user = is_manager(request.user)
    is_shop_user = is_shop(request.user)

    context = {
        'is_manager': is_manager_user,
        'is_shop': is_shop_user
    }
    return render(request, 'home.html', context)

@login_required
def voucher_details(request, code):
    # Sprawdzamy, do jakiej grupy należy użytkownik
    is_manager_user = is_manager(request.user)

    # Pobieramy voucher na podstawie kodu
    if is_manager_user:
        # Managerowie mogą zobaczyć dowolny voucher (również zrealizowany)
        voucher = get_object_or_404(Voucher, code=code)
    else:
        # Pozostali użytkownicy mogą zobaczyć tylko niezrealizowane vouchery
        voucher = get_object_or_404(Voucher, code=code, is_redeemed=False)

    # Przekazanie kontekstu do szablonu
    context = {
        'voucher': voucher,
        'is_manager': is_manager_user,
        'from_list': request.GET.get('from_list') == 'true'
    }

    return render(request, 'voucher_details.html', context)

@login_required
def redeem_voucher(request, code):
    # Pobranie vouchera na podstawie kodu
    voucher = get_object_or_404(Voucher, code=code, is_redeemed=False)

    # Oznaczamy voucher jako zrealizowany
    voucher.is_redeemed = True
    voucher.redeemed_at = timezone.now()
    voucher.redeemed_by = request.user
    voucher.save()

    # Sprawdzamy czy użytkownik jest managerem, aby móc wyświetlić odpowiednie przyciski w szablonie
    is_manager_user = is_manager(request.user)

    return render(request, 'voucher_redeemed.html', {
        'voucher': voucher,
        'is_manager': is_manager_user
    })

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

@login_required
@user_passes_test(is_manager)
def voucher_list(request):
    # Pobierz wszystkie vouchery, sortowane od najnowszych
    vouchers = Voucher.objects.all().order_by('-created_at')

    # Kod do regeneracji kodów QR - zakomentowany, był potrzebny tylko przy pierwszym uruchomieniu
    # print("Regeneracja kodów QR rozpoczęta...")
    # for voucher in vouchers:
    #     print(f"Regeneruję kod QR dla vouchera: {voucher.code}")
    #     voucher.generate_qr_code()
    # print("Regeneracja kodów QR zakończona.")

    # Paginacja - wyświetlamy maksymalnie 10 voucherów na jednej stronie
    paginator = Paginator(vouchers, 10)

    # Pobierz numer strony z parametru GET
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'voucher_list.html', {
        'page_obj': page_obj,
        'is_manager': True
    })