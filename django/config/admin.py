from django.contrib import admin


from config.models import Station, Relay, MusicDirectory

from utils.superuser_required_admin import (
    StaffReadOnlyMixin,
    SuperuserRequiredAdminMixin,
)


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    readonly_fields = ("events_to_next_request",)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Relay)
class RelayAdmin(admin.ModelAdmin, SuperuserRequiredAdminMixin):
    pass


@admin.register(MusicDirectory)
class MusicDirectoryAdmin(admin.ModelAdmin, StaffReadOnlyMixin):
    pass
