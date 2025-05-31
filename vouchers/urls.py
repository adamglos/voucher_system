# vouchers/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('show/', views.show_voucher, name='show_voucher'),
    path('create/', views.create_voucher, name='create_voucher'),
    path('created/', views.voucher_created, name='voucher_created'),
    path('recent/', views.recently_redeemed_vouchers, name='recently_redeemed_vouchers'),
    path('details/<str:code>/', views.voucher_details, name='voucher_details'),
    path('redeem/<str:code>/', views.redeem_voucher, name='redeem_voucher'),
    path('login/', views.custom_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
