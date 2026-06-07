from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, TelegramOTP


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "name", "auth_method", "is_telegram_verified", "is_staff", "is_active", "date_joined")
    list_filter = ("is_staff", "is_active", "auth_method", "is_telegram_verified")
    search_fields = ("email", "name", "phone_number", "telegram_username")
    ordering = ("-date_joined",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Shaxsiy ma'lumotlar", {"fields": ("name", "bio", "avatar")}),
        ("Telegram", {"fields": ("phone_number", "telegram_id", "telegram_username", "is_telegram_verified")}),
        ("Auth", {"fields": ("auth_method",)}),
        ("Ruxsatlar", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Sanalar", {"fields": ("date_joined", "last_login")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "name", "password1", "password2"),
        }),
    )
    readonly_fields = ("date_joined", "last_login")


@admin.register(TelegramOTP)
class TelegramOTPAdmin(admin.ModelAdmin):
    list_display = ("phone_number", "telegram_id", "code", "is_used", "created_at", "expires_at")
    list_filter = ("is_used",)
    search_fields = ("phone_number", "telegram_username")
    readonly_fields = ("created_at",)
