from django.contrib import admin


from misc.models import Donation, ListenerCount

from utils.superuser_required_admin import (
    StaffReadOnlyMixin,
    SuperuserRequiredAdminMixin,
)


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin, SuperuserRequiredAdminMixin):
    pass


@admin.register(ListenerCount)
class ListenerCountAdmin(admin.ModelAdmin, StaffReadOnlyMixin):
    pass
