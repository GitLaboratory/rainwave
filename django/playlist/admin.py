from django.contrib import admin


from playlist.models import Album, Artist, Group, Song, ScanError


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    pass


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    pass


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    pass


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    pass


@admin.register(ScanError)
class ScanErrorAdmin(admin.ModelAdmin):
    pass
