from django.contrib import admin
from .models import Master, Style, Sketch, Client, Session

@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    """Администрирование мастеров."""
    list_display = ['id', 'name', 'expirience_years', 'hourly_rate']
    search_fields = ['name']

@admin.register(Style)
class StyleAdmin(admin.ModelAdmin):
    """Администрирование стилей."""
    list_display = ['id', 'title', 'description']
    search_fields = ['title']

@admin.register(Sketch)
class SketchAdmin(admin.ModelAdmin):
    """Администрирование эскизов."""
    list_display = ['id', 'master', 'title', 'style', 'is_available']
    search_fields = ['title']

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """Администрирование клиентов."""
    list_display = ['id', 'name', 'phone_number']
    search_fields = ['name']

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    """Администрирование сессий."""
    list_display = ['id', 'client', 'master', 'sketch', 'date', 'time', 'status']
    search_fields = ['client__name', 'master__name', 'sketch__title']
    list_filter = ['client', 'master', 'sketch']