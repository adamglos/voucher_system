# vouchers/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Voucher
from django.conf import settings
import os

@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = ('code', 'amount', 'description', 'is_redeemed', 'created_at', 'redeemed_at', 'redeemed_by_username', 'qr_code_preview')
    list_filter = ('is_redeemed', 'created_at', 'redeemed_by')
    search_fields = ('code', 'description', 'redeemed_by__username')

    def has_add_permission(self, request):
        return False

    def redeemed_by_username(self, obj):
        if obj.redeemed_by:
            return obj.redeemed_by.username
        return '-'

    redeemed_by_username.short_description = 'Zrealizowany przez'

    def qr_code_preview(self, obj):
        if obj.qr_code_url():
            return format_html('<img src="{}" width="100" height="100" />', obj.qr_code_url())
        return "(Brak kodu QR)"

    qr_code_preview.short_description = "Podgląd kodu QR"

    def delete_model(self, request, obj):
        # Usuwanie pliku QR przy usuwaniu pojedynczego vouchera
        qr_path = os.path.join(settings.MEDIA_ROOT, f'qr_codes/{obj.code}.png')
        if os.path.exists(qr_path):
            os.remove(qr_path)
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        # Usuwanie plików QR przy usuwaniu wielu voucherów z listy
        for obj in queryset:
            qr_path = os.path.join(settings.MEDIA_ROOT, f'qr_codes/{obj.code}.png')
            if os.path.exists(qr_path):
                os.remove(qr_path)
        super().delete_queryset(request, queryset)
