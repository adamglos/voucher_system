# vouchers/models.py
import qrcode
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model
import os


class Voucher(models.Model):
    code = models.CharField(max_length=12, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    product = models.CharField(max_length=100, blank=True, null=True)
    is_redeemed = models.BooleanField(default=False)
    redeemed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    redeemed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='redeemed_vouchers')

    def generate_qr_code(self):
        try:
            # Tworzymy kod QR na podstawie kodu vouchera
            qr = qrcode.make(self.code)
            # Definiujemy ścieżkę do pliku, w którym chcemy zapisać kod QR
            qr_path = os.path.join(settings.MEDIA_ROOT, f'qr_codes/{self.code}.png')
            # Tworzymy katalog, jeśli nie istnieje
            os.makedirs(os.path.dirname(qr_path), exist_ok=True)
            # Zapisujemy kod QR jako obraz PNG
            qr.save(qr_path)
            return qr_path  # Zwracamy ścieżkę pliku, jeśli zapis się uda
        except Exception as e:
            # Obsługa błędu zapisu – np. zapisywanie błędu w logach lub zwracanie None
            print(f"Błąd przy zapisie kodu QR: {e}")
            return None  # Zwracamy None, jeśli wystąpił błąd

    def qr_code_url(self):
        return f'{settings.MEDIA_URL}qr_codes/{self.code}.png'

    def redeem(self, user=None):
        self.is_redeemed = True
        self.redeemed_at = timezone.now()
        self.redeemed_by = user
        self.save()

    def __str__(self):
        return f'Voucher {self.code}'
