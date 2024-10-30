# vouchers/urls.py
from django.urls import path
from . import views  # Upewnij się, że tutaj importujesz `views` z aplikacji vouchers

urlpatterns = [
    path('', views.home, name='home'),
    path('redeem/', views.redeem_voucher, name='redeem_voucher'),
    path('create/', views.create_voucher, name='create_voucher'),
    path('recent/', views.recently_redeemed_vouchers, name='recently_redeemed_vouchers'),
    path('voucher_created/', views.voucher_created, name='voucher_created'),
]