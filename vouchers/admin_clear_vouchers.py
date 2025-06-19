from django.contrib import admin, messages
from django.urls import path
from django.shortcuts import redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views import View
from .models import Voucher
import os
from django.conf import settings

class ClearVouchersView(View):
    @method_decorator(staff_member_required)
    def get(self, request):
        if not request.user.is_superuser:
            messages.error(request, 'Brak uprawnień do usuwania voucherów!')
            return redirect('/admin/')
        # Usuwanie plików QR
        for voucher in Voucher.objects.all():
            qr_path = os.path.join(settings.MEDIA_ROOT, f'qr_codes/{voucher.code}.png')
            if os.path.exists(qr_path):
                os.remove(qr_path)
        Voucher.objects.all().delete()
        messages.success(request, 'Wszystkie vouchery zostały usunięte!')
        return redirect('/admin/')

# Dodanie URL do admina
if not hasattr(admin.site, '_original_get_urls_vouchers'):
    admin.site._original_get_urls_vouchers = admin.site.get_urls
    def get_urls_with_clear_vouchers():
        urls = admin.site._original_get_urls_vouchers()
        custom_urls = [
            path('clear-vouchers/', admin.site.admin_view(ClearVouchersView.as_view()), name='clear_vouchers'),
        ]
        return custom_urls + urls
    admin.site.get_urls = get_urls_with_clear_vouchers
