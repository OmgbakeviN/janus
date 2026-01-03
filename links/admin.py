from django.contrib import admin
from .models import ShortLink, ClickEvent

# Register your models here.
@admin.register(ShortLink)
class ShortLinkAdmin(admin.ModelAdmin):
    """
    Petite configuration pour voir facilement les liens dans /admin.
    """
    list_display = ("id", "owner", "slug", "original_url", "is_active", "created_at")
    search_fields = ("slug", "original_url", "owner__username")
    list_filter = ("is_active", "created_at")

@admin.register(ClickEvent)
class ClickEventAdmin(admin.ModelAdmin):
    """
    Petite configuration pour voir facilement les clics dans /admin.
    """
    list_display = ("id", "link", "clicked_at", "visitor_id", "ip_address", "user_agent", "referrer", "accept_language")
    search_fields = ("link__slug", "visitor_id", "ip_address")
    list_filter = ("clicked_at", "visitor_id")