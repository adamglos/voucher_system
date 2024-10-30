# vouchers/urls.py
from django.urls import path
from . import views  # Upewnij się, że tutaj importujesz `views` z aplikacji vouchers

urlpatterns = [
    path('redeem/', views.redeem_voucher, name='redeem_voucher'),
    path('create/', views.create_voucher, name='create_voucher'),
    path('voucher_created/', views.voucher_created, name='voucher_created'),  # Dodaj ten URL
]