from django.contrib import admin

from schedule.models import Event, Producer


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    pass


@admin.register(Producer)
class ProducerAdmin(admin.ModelAdmin):
    pass
