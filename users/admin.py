from django.contrib import admin
from .models import Item, Profile


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "stock", "color_variant", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("title", "description", "color_variant")
    list_editable = ("is_active",)
    ordering = ("-created_at",)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "avatar", "created_at")
    search_fields = ("user__username", "user__email")
