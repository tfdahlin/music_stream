import os, random, eyed3, os.path, time, io
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from django.shortcuts import render, redirect
from wsgiref.util import FileWrapper
from django.http import HttpResponse, JsonResponse
from .models import Song, Artist, Album, Playlist
from django.contrib.auth.decorators import login_required, permission_required
from user.views import login as custom_login
from main.logging import Log
from django.conf import settings
from PIL import Image
from wakeonlan import send_magic_packet


# Create your views here.
def index(request):
    # we should only get post requests on this page if a user is logging in
    if(request.method == 'POST'):
        return custom_login(request)
    else: # default behavior, return the main page
        try:
            song_id = request.GET.get('songid')
            if(not song_id.isdigit()): # Avoid sql injection by making sure the song_id is a digit
                logcontext = {'value': song_id}
                if request.user.get_username() != "":
                    logcontext['username'] = request.user.get_username()
                else:
                    logcontext['username'] = "Guest"
                Log.attemptedSQLInjection(logcontext)
                song_id = None
        except:
            song_id = None

        if(song_id != None):
            try:
                song = Song.objects.get(id=song_id)
            except:
                song_title = None
                song_artist = None
                song_album = None
            else:
                song_title = song.name
                try:
                    song_artist = song.artist.name
                except:
                    song_artist = None
                try:
                    song_album = song.album.name
                except:
                    song_album = None
        else:
            song_title = None
            song_artist =  None
            song_album = None
            
        base_folder = settings.MUSIC_FOLDER
        playlist_id = request.GET.get('playlist_id')
        if playlist_id == None:
            songs = Song.objects.filter().order_by('artist__name', 'album__name', 'name')
            song_count = songs.count()
            print("All songs. Song count: " + str(song_count))
            is_all_songs = True
        else:
            songs = Song.objects.filter(playlists__id=playlist_id)
            song_count = songs.count()
            print("Song count: " + str(song_count))
            is_all_songs = False
            if(songs.count() == 0):
                print("No songs found in playlist.")
                return redirect('main:index')
        if(request.user.is_authenticated):
            volume = int(request.user.volume*100)
            try:
                playlist = Playlist.objects.get(id=playlist_id)
                if(playlist.owner == request.user):
                    is_owner = True
                else:
                    is_owner = False
            except:
                playlist = None
                is_owner = None
            my_playlists = Playlist.objects.filter(owner=request.user).order_by('name')
            all_playlists = Playlist.objects.filter(public=True).exclude(song=None).order_by('name') | Playlist.objects.filter(owner=request.user).order_by('name')
            if not all_playlists:
                all_playlists = None
            print(request.user.get_username() + " has loaded the homepage.")
        else:
            volume = None
            try:
                playlist = Playlist.objects.get(id=playlist_id)
            except:
                playlist = None
            is_owner = None
            my_playlists = None
            all_playlists = Playlist.objects.filter(public=True).exclude(song=None).order_by('name')
            if not all_playlists:
                all_playlists = None
            print("Guest has loaded the homepage.")
        nonce = str(generate_nonce())
        context = {
            'song_title': song_title,
            'song_album': song_album,
            'song_artist': song_artist,
            'song_count': song_count,
            'user': request.user,
            'my_playlists': my_playlists,
            'all_playlists': all_playlists,
            'playlist': playlist,
            'is_owner': is_owner,
            'song_id': song_id,
            'nonce': nonce,
            'volume': volume,
            'url': settings.WEBSITE_URL,
            'site_name': settings.WEBSITE_NAME,
            'showcase': False, # ONLY SET TO TRUE WHEN SHARING WITH RECRUITERS
        }
        response = render(request, 'main/index.html', context)
        response['Content-Security-Policy'] = "script-src \'self\' \'nonce-"+nonce+"\' https://code.jquery.com/jquery-3.3.1.min.js"
        response['X-XSS-Protection'] = "1; mode=block"
        return response
        
def generate_nonce(length=20):
    #Generate pseudorandom number.
    return ''.join([str(random.randint(0, 9)) for i in range(length)])
    
    
@login_required(login_url="login:login")
def remember_volume(request):
    volume = request.GET['volume']
    request.user.volume = volume
    request.user.save()
    return HttpResponse("Volume preference updated to" + str(volume))
    
@login_required
def refresh(request):
    if(not get_last_refresh_time()):
        #print("It has not been at least one hour since last refresh.")
        return index(request)
    if(request.user.can_control == True):
        base_folder = settings.MUSIC_FOLDER
        
        Log.logUpdateStart()
        os.system(settings.MOUNT_SHARE_SCRIPT)
        update_database(base_folder)
        
        Log.logUpdateFinished()
        cache_filename = settings.LIBRARY_CACHE_FILENAME
        cache_available = False
        # if the file exists
        if(os.path.isfile(cache_filename)):
            os.remove(cache_filename)
    else:
        print("User doesn't have permission.")
    
    return index(request)

@login_required
def restart(request):
    if(not get_last_restart_time()):
        print("It has not been at least one hour since last restart.")
        return index(request)
    if(request.user.can_control == True):
        send_magic_packet(settings.MAGIC_PACKET_MAC_ADDRESS)
        os.system(settings.SERVER_RESTART_SCRIPT)
    else:
        print("User doesn't have permission.")
    return index(request)

def update_database(base_folder):
    for file in os.listdir(base_folder):
        filename = base_folder + '/' + file
        if(not(os.path.isfile(filename))):
            update_database(filename)
        else:
            if(filename.endswith('.mp3')):
                add_song(base_folder, file)
    return

def add_song(base_folder, file):
    filename = base_folder + '/' + file
    try: # if the song is already in the database, skip it
        song_instance = Song.objects.get(filepath=str(filename[18:]))
        return
    except:
        print(filename + " not in database.")
        if(filename.endswith('.mp3')):
            # load the audio file to update the database
            try:
                audiofile = eyed3.load(filename)
            except:
                print("Could not open file: ",end="")
                print(filename)
            else:
                if(audiofile == None):
                    print("Could not open file: ",end="")
                    print(filename)
                    return
                try:
                    song_name = audiofile.tag.title
                    artist_name = audiofile.tag.artist
                    album_name = audiofile.tag.album
                except:
                    print("Error processing tags of file: ",end="")
                    print(filename)
                    return
                
                # create a new database entry
                new_song = Song()
                
                # update the entry's filepath
                new_song.filepath = filename[18:]
                audio = MP3(filename)
                min, sec = divmod(int(audio.info.length), 60)
                hr, min = divmod(min, 60)
                if(hr > 0):
                    new_song.track_length = "%02d:%02d:%02d" % (hr, min, sec)
                else:
                    new_song.track_length = "%02d:%02d" % (min, sec)
                
                # try adding the title; if we can't, it shouldn't be in the database
                try:
                    new_song.name = audiofile.tag.title
                except:
                    print("ERROR: Could not add file: ",end="")
                    print(filename)
                    return
                    
                # try adding the artist; create new artist entry if necessary
                if(audiofile.tag.artist != None):
                    try:
                        artist_instance = Artist.objects.get(name=artist_name)
                        new_song.artist = artist_instance
                    except:
                        new_artist = Artist()
                        new_artist.name = audiofile.tag.artist
                        new_artist.save()
                        new_song.artist = Artist.objects.get(name=artist_name)
                    
                # try adding the album; create new album entry if necessary
                if(audiofile.tag.album != None):
                    try:
                        album_instance = Album.objects.get(name=album_name)
                        new_song.album = album_instance
                    except:
                        new_album = Album()
                        new_album.name = audiofile.tag.album
                        new_album.save()
                        new_song.album = Album.objects.get(name=album_name)
                new_song.save()
    return

def replace_songid(request):
    count = Song.objects.all().count()
    rnum = random.randint(1,count)
    while(not Song.objects.filter(id=rnum).exists()):
        rnum = random.randint(1,count)
    if not request.GET._mutable:
        request.GET._mutable = True
    print("Getting new songid: " + str(rnum))
    request.GET['songid'] = str(rnum)
    
def get_song(request):
    os.system(settings.MOUNT_SHARE_SCRIPT)
    try:
        songid = request.GET.get('songid')
        if(not songid.isdigit()): # avoid sql injection
            print("Attempted SQL Injection")
            logcontext = {}
            if(request.user.get_username != ""):
                logcontext['username'] = request.user.get_username()
            else:
                logcontext['username'] = "Guest"
            logcontext['value'] = songid
            
            Log.attemptedSQLInjection(logcontext)
            replace_songid(request)
            
            return get_song(request)
            
        song = Song.objects.get(id=songid)
        # Update song info 
        filename = Song.objects.get(id=songid).filepath
        myfile = settings.MUSIC_FOLDER + filename
        try:
            audiofile = eyed3.load(myfile)
        except:
            errorcontext = {}
            errorcontext['filename'] = myfile
            Log.logFileMissing(errorcontext)
            song.delete()
            replace_songid(request)
            return get_song(request)
        updated = False
        try:
            try:
                if(audiofile.tag.title != None):
                    if(audiofile.tag.title != song.name):
                        song.name = audiofile.tag.title
                        updated = True
            except:
                print("Failed to find track title.")
            try:
                if(audiofile.tag.artist != None):
                    if((song.artist == None) or (audiofile.tag.artist != song.artist.name)):
                        try:
                            artist_instance = Artist.objects.get(name=audiofile.tag.artist)
                            song.artist = artist_instance
                        except:
                            new_artist = Artist()
                            new_artist.name = audiofile.tag.artist
                            new_artist.save()
                            song.artist = Artist.objects.get(name=audiofile.tag.artist)
                        updated = True
            except:
                print("Failed to find track artist.")
            try:
                if(audiofile.tag.album != None):
                    if((song.album == None) or (audiofile.tag.album != song.album.name)):
                        print("Song album updated.")
                        try:
                            album_instance = Album.objects.get(name=audiofile.tag.album)
                            song.album = album_instance
                        except:
                            new_album = Album()
                            new_album.name = audiofile.tag.album
                            new_album.save()
                            song.album = Album.objects.get(name=audiofile.tag.album)
                        updated = True
            except:
                print("Failed to find track album.")
        except:
            print("Failed to update.")
        finally:
            if updated:
                song.save()
        
        if(myfile.endswith('.mp3')):
            now_playing = "Now playing"
            if(request.user.get_username() != ""):
                now_playing += " (" + request.user.get_username() + ")"
            else:
                now_playing += " (Guest)"
            try:
                if(song.name != None):
                    now_playing += ": " + song.name
                    if(song.artist.name != None):
                        now_playing += " by " + song.artist.name
            except:
                print("Error fetching title or artist")
            print("")
            print(now_playing)
            print("")
            wrapper = FileWrapper(open( myfile, "rb" ))
            response = HttpResponse(wrapper, content_type='audio/mpeg')
            response['Content-Length'] = os.path.getsize( myfile )
            response['Accept-Ranges'] = "bytes"
            return response
        else:
            replace_songid(request)
            return get_song(request)
    except:
        print("Exception while getting song :C")
        replace_songid(request)
        return get_song(request)

def fetch_album_artwork(request):
    try:
        songid = request.GET.get('songid')
        if(not songid.isdigit()): # avoid sql injection
            myfile = os.path.dirname(os.path.realpath(__file__)) + '/album-art-missing.png'
            with open(myfile, "rb") as f:
                return HttpResponse(f.read(), content_type="image/png")
        song = Song.objects.get(id=songid)
        filename = Song.objects.get(id=songid).filepath
        folder = settings.MUSIC_FOLDER + filename
        while(folder[-1] != '/'):
            folder = folder[:-1]
        for fname in os.listdir(folder):
            if fname.endswith('.png'):
                filepath = folder + fname
                with open(filepath, "rb") as f:
                    return HttpResponse(f.read(), content_type="image/png")
            if fname.endswith('.jpg'):
                filepath = folder + fname
                with open(filepath, "rb") as f:
                    return HttpResponse(f.read(), content_type="image/jpeg")
            if fname.endswith('.webp'):
                print("Converting artwork")
                filepath = folder + fname
                im = Image.open(filepath).convert("RGB")
                imagebytes = io.BytesIO()
                im.save(imagebytes, format="png")
                return HttpResponse(imagebytes.getvalue(), content_type="image/png")
        raise Exception("Error finding album artwork")
    except Exception as e:
        print(e)
        context = {}
        if(song.name != None):
            context['song'] = song.name
        else:
            context['song'] = None
        if(song.album != None and song.album.name != None):
            context['album'] = song.album.name
        else:
            context['album'] = None
        if(song.artist != None and song.artist.name != None):
            context['artist'] = song.artist.name
        else:
            context['artist'] = None
        Log.logMissingArtwork(context)
        myfile = os.path.dirname(os.path.realpath(__file__)) + '/album-art-missing.png'
        with open(myfile, "rb") as f:
            return HttpResponse(f.read(), content_type="image/png")
        
def fetch_track_info(request):
    songid = request.GET.get('songid')
    response = {}
    if(not songid.isdigit()): # avoid sql injection
        return JsonResponse(response)
    try:
        song_instance = Song.objects.get(id=songid)
        if(song_instance.name != None):
            response['title'] = song_instance.name
        if(song_instance.album != None and song_instance.album.name != None):
            response['album'] = song_instance.album.name
        if(song_instance.artist != None and song_instance.artist.name != None):
            response['artist'] = song_instance.artist.name
        response['songid'] = songid
        return JsonResponse(response)
        
    except:
        print("Exception. Returning empty json")
        return JsonResponse(response)
        
@login_required(login_url="login:login")        
def add_to_playlist(request):
    try:
        if(request.method!="GET"):
            print("Method is not GET.")
            return redirect('main:index')
        
        playlist_id = request.GET.get('playlist_id')
        songid = request.GET.get('songid')
        
        if((not songid.isdigit()) or (not playlist_id.isdigit())): # avoid SQL injection
            print("Songid or playlist id is not a digit.")
            return redirect('main:index')
        print("Trying to add song " + str(songid) + " to playlist " + str(playlist_id))
        playlist_exists = Playlist.objects.filter(id=playlist_id).exists()
        song_exists = Song.objects.filter(id=songid).exists()
        
        if playlist_exists and song_exists:
            playlist = Playlist.objects.get(id=playlist_id)
            song = Song.objects.get(id=songid)
            if (playlist.owner != request.user):
                print("Playlist " + playlist.name + " does not belong to user " + request.user.username)
                return HttpResponse("ERROR")
            if song not in playlist.song_set.all():
                song.playlists.add(playlist)
                print("Adding " + song.name + " to playlist " + playlist.name)
            else:
                print("Tried adding a duplicate!")
            return HttpResponse("SUCCESS")
        else:
            print("Playlist or song does not exist")
            return HttpResponse("ERROR")
    except:
        print("Exception encountered while adding to playlist")
        return redirect('main:index')

@login_required(login_url="login:login")
def remove_from_playlist(request):
    try:
        if(request.method != "GET"):
            return redirect('main:index')
        playlist_id = request.GET.get('playlist_id')
        songid = request.GET.get('songid')
        if((not songid.isdigit()) or (not playlist_id.isdigit())): # avoid SQL injection
            return redirect('main:index')
        
        playlist_exists = Playlist.objects.filter(id=playlist_id).exists()
        song_exists = Song.objects.filter(id=songid).exists()
        
        if playlist_exists and song_exists:
            playlist = Playlist.objects.get(id=playlist_id)
            song = Song.objects.get(id=songid)
            if(playlist.owner != request.user):
                print("Playlist " + playlist.name + " does not belong to user " + request.user.username)
                return HttpResponse("ERROR")
            if song not in playlist.song_set.all():
                print("Song does not exist in this playlist!")
                return HttpResponse("ERROR")
            else:
                song.playlists.remove(playlist)
                print("Removing " + song.name + " from playlist " + playlist.name)
                return HttpResponse("ERROR")
        else:
            print("Playlist or song does not exist")
            return HttpResponse("ERROR")
    except:
        print("Exception encountered while removing track from playlist")
        return redirect('main:index')

@login_required(login_url="login:login")        
def create_playlist(request):
    try:
        if(request.method != "GET"):
            print("Non-GET request made to create_playlist")
            return redirect('main:index')
        playlist_name = request.GET.get('playlist_name')
        
        # TODO: JAVASCRIPT TO MAKE SURE THAT PLAYLIST NAME DOESN'T EXIST ALREADY
        if(Playlist.objects.filter(name=playlist_name, owner__username=request.user.username).exists()):
            print("Playlist " + playlist_name + " already exists")
            return redirect('main:index')
        else:
            new_playlist = Playlist(name=playlist_name, owner=request.user)
            new_playlist.save()
            print("Created new playlist: " + playlist_name + " belonging to user " + request.user.username)
            return redirect('main:index')
    except:
        print("Exception encountered while creating playlist")
        return redirect('main:index')

@login_required(login_url="login:login")
def edit_playlists(request):
    if(request.method == 'POST'):
        elements = request.POST.dict()
        del elements['csrfmiddlewaretoken']
        my_playlists = Playlist.objects.filter(owner__username=request.user.username)
        print("Got playlists.")
        for playlist in my_playlists:
            playlist.public = False
            playlist.save()
        for key, value in elements.items():
            if(value=="on"):
                try:
                    playlist = Playlist.objects.get(id=int(key))
                    if(playlist.owner.username == request.user.username):
                        playlist.public = True
                        playlist.save()
                except:
                    pass
    my_playlists = Playlist.objects.filter(owner=request.user).order_by('name')
    context = {
        'playlists': my_playlists,
    }
    return render(request, 'main/playlists.html', context)

@login_required(login_url="login:login")
def edit_profile(request):
    if(request.method == 'POST'):
        elements = request.POST.dict()
        del elements['csrfmiddlewaretoken']
        if 'name' in elements:
            request.user.name = elements['name']
            request.user.save()
    context = {}
    return render(request, 'main/profile.html', context)

def get_random_song(request):
    print("Getting random song...")
    response = {}
    playlist_id = request.GET.get('playlist_id')
    if playlist_id == None:
        songs = Song.objects.filter().order_by('artist__name', 'album__name', 'name')
    else:
        songs = Song.objects.filter(playlists__id=playlist_id)
        if(songs.count() == 0):
            print("No songs found in playlist.")
            return JsonResponse(response)

    song = songs.order_by('?').first()
    current_track_id = request.GET.get('current_track')
    if (songs.count() > 1) and (current_track_id != None):
        if str(song.id) == current_track_id:
            return get_random_song(request)
    response['src'] = "get_song?songid=" + str(song.id)
    response['title'] = song.name
    if((song.artist != None) and (song.artist.name != None)):
        response['artist'] = song.artist.name
    if((song.album != None) and (song.album.name != None)):
        response['album'] = song.album.name
    response['songid'] = str(song.id)
    return JsonResponse(response)
    

def load_playlist(request):
    base_folder = settings.MUSIC_FOLDER
    playlist_id = request.GET.get('playlist_id')
    if((playlist_id == None) or (playlist_id == '')):
        songs = Song.objects.filter().order_by('artist__name', 'album__name', 'name')
        is_all_songs = True
        print("Loading all songs.")
    else:
        print("Loading playlist with id: " + playlist_id)
        is_all_songs = False
        songs = Song.objects.filter(playlists__id=playlist_id)
        if(songs.count() == 0):
            print("No songs found in playlist.")
            if not request.GET._mutable:
                request.GET._mutable = True
            request.GET['playlist_id'] = None
            return load_playlist(request)

    context = {
        'all_songs': songs,
    }
    if(is_all_songs):
        return get_cache_or_render(request, context)
    response = render(request, 'main/music_list.html', context)
    return response

def get_cache_or_render(request, context):
    cache_filename = settings.LIBRARY_CACHE_FILENAME
    cache_available = False
    # if the file exists
    if(os.path.isfile(cache_filename)):
        last_modified = os.path.getmtime(cache_filename)
        last_modified = time.gmtime(last_modified)
        # if the file was made today
        if(not is_date_older(last_modified)):
            cache_available = True
    if(not cache_available):
        return update_file(request, context)
    else:
        with open(cache_filename, "rb") as f:
            return HttpResponse(f.read())

def update_file(request, context):
    response = render(request, 'main/music_list.html', context)
    cache_filename = settings.LIBRARY_CACHE_FILENAME
    f = open(cache_filename, "wb+")
    f.write(response.content)
    f.close()
    return response

def get_last_restart_time():
    cache_filename = settings.LAST_RESTART_CACHE_FILENAME
    if(os.path.isfile(cache_filename)):
        last_modified = os.path.getmtime(cache_filename)
        curr_time = time.time()
        if(curr_time - last_modified > 600):
            touch_command = "touch " + cache_filename
            os.system(touch_command)
            return True
    else:
        touch_command = "touch " + cache_filename
        os.system(touch_command)
        return True
    return False

def get_last_refresh_time():
    cache_filename = settings.LAST_REFRESH_CACHE_FILENAME
    if(os.path.isfile(cache_filename)):
        last_modified = os.path.getmtime(cache_filename)
        curr_time = time.time()
        if(curr_time - last_modified > 60):
            touch_command = "touch " + cache_filename
            os.system(touch_command)
            return True
    else:
        touch_command = "touch " + cache_filename
        os.system(touch_command)
        return True
    return False

def is_date_older(old):
    current = time.gmtime()
    current_day = current.tm_mday
    current_month = current.tm_mon
    current_year = current.tm_year
    old_day = old.tm_mday
    old_month = old.tm_mon
    old_year = old.tm_year
    
    if((old_day < current_day) or (old_month < current_month) or (old_year < current_year)):
        return True
    return False
