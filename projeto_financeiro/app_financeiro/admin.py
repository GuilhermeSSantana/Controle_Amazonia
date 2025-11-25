from django.contrib import admin
from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "document", "type", "email", "phone", "is_active", "created_at")
    list_filter = ("type", "is_active")
    search_fields = ("name", "document", "email")
