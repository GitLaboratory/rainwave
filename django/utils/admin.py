from django.contrib import admin


class NoAddOrDeleteModelAdmin(admin.ModelAdmin):
    def has_add_permission(self, *args, **kwargs):
        return False

    def has_delete_permission(self, *args, **kwargs):
        return False


class NoAddOrDeleteTabularInline(admin.TabularInline):
    extra = 0

    def has_add_permission(self, *args, **kwargs):
        return False

    def has_delete_permission(self, *args, **kwargs):
        return False
