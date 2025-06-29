# vouchers/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('show/', views.show_voucher, name='show_voucher'),
    path('create/', views.create_voucher, name='create_voucher'),
    path('created/<str:code>/', views.voucher_created, name='voucher_created'),
    path('recent/', views.recently_redeemed_vouchers, name='recently_redeemed_vouchers'),
    path('details/<str:code>/', views.voucher_details, name='voucher_details'),
    path('redeem/<str:code>/', views.redeem_voucher, name='redeem_voucher'),
    path('login/', views.custom_login, name='login'),
    path('all-vouchers/', views.voucher_list, name='voucher_list'),
    path('not-found/', views.voucher_not_found, name='voucher_not_found'),
]
