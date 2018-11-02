from django.contrib import admin
from django.urls import path, include

from .views import (
    index,
    get_song,
    refresh,
    restart,
    add_to_playlist,
    create_playlist,
    edit_playlists,
    edit_profile,
    remove_from_playlist,
    fetch_track_info,
    fetch_album_artwork,
    remember_volume,
    load_playlist,
    get_random_song,
)

from user.views import (
    logout_view,
)

app_name = 'main'

urlpatterns = [
    path(r'', index, name='index'),
    path(r'get_playlist_songs/', load_playlist, name='load_playlist'),
    path(r'get_random_song', get_random_song, name='get_random_song'),
    path(r'get_song', get_song, name='get_song'),
    path(r'refresh', refresh, name='refresh'),
    path(r'restart', restart, name='restart'),
    path(r'logout', logout_view, name='logout'),
    path(r'add_to_playlist', add_to_playlist, name='add_to_playlist'),
    path(r'remove_from_playlist', remove_from_playlist, name='remove_from_playlist'),
    path(r'create_playlist', create_playlist, name='create_playlist'),
    path(r'playlists', edit_playlists, name='edit_playlists'),
    path(r'profile', edit_profile, name='edit_profile'),
    path(r'fetch_track_info', fetch_track_info, name='fetch_track_info'),
    path(r'fetch_album_artwork', fetch_album_artwork, name='fetch_album_artwork'),
    path(r'update_volume', remember_volume, name='remember_volume'),
]
