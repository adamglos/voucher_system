from django.contrib.admin.models import LogEntry
from django.contrib import admin, messages
from django.urls import path
from django.shortcuts import redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views import View

class ClearAdminLogView(View):
    @method_decorator(staff_member_required)
    def get(self, request):
        if not request.user.is_superuser:
            messages.error(request, 'Brak uprawnień do czyszczenia logów!')
            return redirect('/admin/')
        LogEntry.objects.all().delete()
        messages.success(request, 'Wyczyszczono listę ostatnich działań!')
        return redirect('/admin/')

# Poprawne nadpisanie get_urls bez rekursji
if not hasattr(admin.site, '_original_get_urls'):
    admin.site._original_get_urls = admin.site.get_urls
    def get_urls_with_clear_log():
        urls = admin.site._original_get_urls()
        custom_urls = [
            path('clear-log/', admin.site.admin_view(ClearAdminLogView.as_view()), name='clear_admin_log'),
        ]
        return custom_urls + urls
    admin.site.get_urls = get_urls_with_clear_log
