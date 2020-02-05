from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from users.models import APIKey, Listener, UserSettings


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    pass


@admin.register(Listener)
class ListenerAdmin(admin.ModelAdmin):
    pass


class SettingsInline(admin.StackedInline):
    model = UserSettings
    readonly_fields = [
        "last_active",
        "listen_key",
        "losing_requests",
        "losing_votes",
        "requests_paused",
        "total_mind_changes",
        "total_ratings",
        "total_requests",
        "total_votes",
        "winning_requests",
        "winning_votes",
    ]


admin.site.unregister(get_user_model())


@admin.register(get_user_model())
class RainwaveUserAdmin(UserAdmin):
    inlines = UserAdmin.inlines + [SettingsInline]
