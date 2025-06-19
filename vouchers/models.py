# vouchers/models.py
import qrcode
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model
import os
from PIL import Image, ImageDraw, ImageFont
import io


class Voucher(models.Model):
    code = models.CharField(max_length=12, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=50, null=False, blank=False)
    is_redeemed = models.BooleanField(default=False)
    redeemed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_vouchers')
    redeemed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='redeemed_vouchers')

    def generate_qr_code(self):
        try:
            # Tworzymy podstawowy kod QR
            qr = qrcode.make(self.code)
            qr_img = qr.get_image()

            # Konwertujemy obraz do formatu PIL Image jeśli jeszcze nim nie jest
            if not isinstance(qr_img, Image.Image):
                qr_img = Image.open(io.BytesIO(qr_img))

            # Pobieramy wymiary kodu QR
            width, height = qr_img.size

            # Dodajemy minimalną przestrzeń na tekst pod kodem QR
            padding = 20  # Jeszcze mniejsza przestrzeń dla tekstu
            new_img = Image.new('RGB', (width, height + padding), 'white')

            # Wklejamy kod QR na górze nowego obrazu
            new_img.paste(qr_img, (0, 0))

            # Dodajemy tekst (kod vouchera) pod kodem QR
            draw = ImageDraw.Draw(new_img)

            # Używamy optymalnej czcionki
            font_size = 20

            # Ścieżka do czcionki Arial w katalogu głównym projektu
            arial_path = os.path.join(settings.BASE_DIR, 'arial.ttf')

            try:
                # Używamy czcionki Arial z katalogu głównego projektu
                font = ImageFont.truetype(arial_path, font_size)
            except Exception as e:
                print(f"Nie można załadować czcionki Arial: {e}")
                # Jeśli nie możemy załadować czcionki Arial, używamy domyślnej
                font = ImageFont.load_default()

            # Tekst do dodania
            text = self.code

            # Obliczamy szerokość tekstu (jeśli metoda jest dostępna)
            if hasattr(draw, 'textlength'):
                text_width = draw.textlength(text, font=font)
            else:
                # Przybliżone obliczenie szerokości tekstu dla czcionki Arial
                text_width = len(text) * (font_size * 0.55)

            # Wyśrodkowanie tekstu w poziomie i przesunięcie go bliżej kodu QR
            text_position = ((width - int(text_width)) // 2, height - font_size)

            # Rysujemy tekst
            draw.text(xy=text_position, text=text, fill='black', font=font)

            # Ścieżka do zapisania pliku
            qr_path = os.path.join(settings.MEDIA_ROOT, f'qr_codes/{self.code}.png')
            # Tworzymy katalog, jeśli nie istnieje
            os.makedirs(os.path.dirname(qr_path), exist_ok=True)
            # Zapisujemy kod QR jako obraz PNG
            new_img.save(qr_path)

            return qr_path

        except Exception as e:
            print(f"Błąd przy zapisie kodu QR: {e}")
            return None

    def qr_code_url(self):
        return f'{settings.MEDIA_URL}qr_codes/{self.code}.png'

    def redeem(self, user=None):
        self.is_redeemed = True
        self.redeemed_at = timezone.now()
        self.redeemed_by = user
        self.save()

    def __str__(self):
        return self.code
