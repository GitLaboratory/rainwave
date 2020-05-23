from django.contrib import admin

from playlist.models import (
    Album,
    AlbumOnStation,
    Artist,
    Group,
    GroupOnStation,
    Song,
    SongOnStation,
    ScanError,
)

from utils.admin import NoAddOrDeleteModelAdmin, NoAddOrDeleteTabularInline


class AlbumOnStationInline(NoAddOrDeleteTabularInline):
    model = AlbumOnStation
    fields = (
        "station",
        "rating",
        "cooldown_multiplier",
        "cooldown_override",
        "permanently_request_only",
    )
    readonly_fields = ("station", "rating")
    ordering = ("station",)

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).select_related("station")


@admin.register(Album)
class AlbumAdmin(NoAddOrDeleteModelAdmin):
    list_display = ("name", "added_on")
    list_display_links = ("name",)
    search_fields = ("name",)
    inlines = (AlbumOnStationInline,)
    readonly_fields = ("name_searchable",)


@admin.register(AlbumOnStation)
class AlbumOnStationAdmin(NoAddOrDeleteModelAdmin):
    list_display = (
        "album",
        "station",
        "newest_song_added_on",
        "rating",
        "cooldown_multiplier",
        "cooldown_override",
        "permanently_request_only",
    )
    list_display_links = ("album",)
    list_editable = (
        "cooldown_multiplier",
        "cooldown_override",
        "permanently_request_only",
    )
    list_filter = (
        "station",
        "rating",
        "cooldown_multiplier",
        "cooldown_override",
        "permanently_request_only",
    )
    ordering = ("station__pk", "album__name")
    search_fields = ("album__name",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("album", "station")


@admin.register(Artist)
class ArtistAdmin(NoAddOrDeleteModelAdmin):
    readonly_fields = ("name_searchable",)


class GroupOnStationInline(NoAddOrDeleteTabularInline):
    model = GroupOnStation
    fields = (
        "station",
        "visible",
    )
    readonly_fields = ("station",)
    ordering = ("station",)

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).select_related("station")


@admin.register(Group)
class GroupAdmin(NoAddOrDeleteModelAdmin):
    readonly_fields = ("name_searchable",)
    inlines = (GroupOnStationInline,)


class SongOnStationInline(NoAddOrDeleteTabularInline):
    model = SongOnStation
    fields = (
        "station",
        "cooldown_multiplier",
        "cooldown_override",
        "permanently_request_only",
    )
    readonly_fields = ("station",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("station")


@admin.register(Song)
class SongAdmin(NoAddOrDeleteModelAdmin):
    readonly_fields = (
        "name",
        "album",
        "origin_station",
        "filename",
        "added_on",
        "fave_count",
        "rating",
        "rating_count",
        "request_count",
        "disc_number",
        "length",
        "link_text",
        "replaygain",
        "track_number",
        "url",
        "year",
    )
    inlines = (SongOnStationInline,)
    list_display = ("name", "album", "origin_station", "permanently_request_only")
    list_editable = ("permanently_request_only",)
    list_filter = ("permanently_request_only",)
    search_fields = ("name", "album__name")
    ordering = ("album__name", "name")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "album",
                    "origin_station",
                    "filename",
                    "rating",
                    "rating_count",
                    "permanently_request_only",
                )
            },
        ),
        (
            "Statistics",
            {
                "classes": ("collapse",),
                "fields": ("added_on", "fave_count", "request_count",),
            },
        ),
        (
            "ID3 Tags",
            {
                "classes": ("collapse",),
                "fields": (
                    "disc_number",
                    "length",
                    "link_text",
                    "replaygain",
                    "track_number",
                    "url",
                    "year",
                ),
            },
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("album", "origin_station")


@admin.register(ScanError)
class ScanErrorAdmin(NoAddOrDeleteModelAdmin):
    fields = ("when", "filename", "error")
    readonly_fields = ("when", "filename", "error")
    list_display = ("id", "filename", "error")
    list_display_links = ("id",)
    ordering = ("-id",)
