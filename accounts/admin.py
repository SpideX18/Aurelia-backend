from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import ActivityLog, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ["email", "username", "role", "is_staff", "date_joined"]
    list_filter = ["role", "is_staff", "is_active"]
    fieldsets = UserAdmin.fieldsets + (("Role & Profile", {"fields": ("role", "phone", "avatar")}),)


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ["user", "action", "created_at"]
    list_filter = ["action"]
    readonly_fields = ["user", "action", "details", "ip_address", "created_at"]
