# vouchers/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Voucher

@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = ('code', 'amount', 'product', 'is_redeemed', 'created_at', 'redeemed_at', 'qr_code_preview')
    list_filter = ('is_redeemed', 'created_at')
    search_fields = ('code', 'product')

    def qr_code_preview(self, obj):
        if obj.qr_code_url():
            return format_html('<img src="{}" width="100" height="100" />', obj.qr_code_url())
        return "(No QR code)"

    qr_code_preview.short_description = "QR Code Preview"
