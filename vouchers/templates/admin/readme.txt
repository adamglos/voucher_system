# Instrukcje dotyczące czcionek w kodach QR

Jeśli czcionka w kodzie QR jest za mała lub nieczytelna, możesz skopiować plik czcionki do folderu projektu:

1. Utwórz folder `static/fonts/` wewnątrz aplikacji `vouchers` (jeśli nie istnieje)
2. Skopiuj plik czcionki (np. Arial.ttf) do tego folderu
3. Zmodyfikuj metodę `generate_qr_code` w pliku `models.py` aby używała tej czcionki

Przykład modyfikacji kodu:

```python
# Zamiast szukać czcionki systemowej, użyj pliku z projektu
try:
    font_path = os.path.join(settings.BASE_DIR, 'vouchers/static/fonts/Arial.ttf')
    font = ImageFont.truetype(font_path, 40)  # Bardzo duży rozmiar (40+)
except Exception as e:
    print(f"Nie można załadować czcionki: {e}")
    font = ImageFont.load_default()
```

Możesz pobrać darmowe czcionki z:
- Google Fonts: https://fonts.google.com/
- Font Squirrel: https://www.fontsquirrel.com/
