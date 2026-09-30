"""
Admin configuration for the accounts application.
"""
from django.contrib import admin

from .models import UserActivityLog, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "gender", "organization", "created_at")
    search_fields = ("user__username", "user__email", "full_name", "organization")
    list_filter = ("gender", "created_at")


@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = ("user", "action", "ip_address", "timestamp")
    search_fields = ("user__username", "action", "details", "ip_address")
    list_filter = ("action", "timestamp")
    readonly_fields = ("user", "action", "details", "ip_address", "timestamp")

    def has_add_permission(self, request):
        return False