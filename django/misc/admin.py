from django.contrib import admin

from misc.models import Donation, ListenerCount, Station, Relay


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    pass


@admin.register(ListenerCount)
class ListenerCountAdmin(admin.ModelAdmin):
    pass


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    pass


@admin.register(Relay)
class RelayAdmin(admin.ModelAdmin):
    pass
