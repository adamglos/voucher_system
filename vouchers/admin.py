# vouchers/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Voucher

@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = ('code', 'amount', 'product', 'is_redeemed', 'created_at', 'redeemed_at', 'redeemed_by_username', 'qr_code_preview')
    list_filter = ('is_redeemed', 'created_at', 'redeemed_by')
    search_fields = ('code', 'product', 'redeemed_by__username')

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
