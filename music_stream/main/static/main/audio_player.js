function updateSoundIcon() {
    var playervol = audio_player.volume;
    var icon = document.getElementById("volume_icon");
    if(playervol < 0.05) {
        icon.src = "/static/main/very_low_volume.png";
    } else if(playervol < 0.5) {
        icon.src = "/static/main/low_volume.png";
    } else {
        icon.src = "/static/main/high_volume.png";
    }
}



function seconds_to_minutes(seconds) {
    var hours = parseInt(seconds/3600);
    var minutes = parseInt((seconds % 3600)/60);
    var seconds = parseInt((seconds % 60));
    var result = "";
    if(hours > 0) {
        result += hours.toString() + ":";
    } 
    if(minutes > 0) {
        if(minutes >= 10) {
            result += parseInt(minutes/10).toString();
        }
        result += (minutes%10).toString() + ":";
    } else {
        result += "0:";
    }
    if(!isNaN(seconds/10) && !isNaN(seconds %10)) {
        result += parseInt(seconds/10) + (seconds%10).toString();
    } else if(!isNaN(seconds/10)) {
        result += "0" + (seconds%10).toString();
    } else {
        result += "00";
    }
    return result;
}

function time_update() {
    var current_time = audio_player.currentTime;
    var total_time = audio_player.duration;
    var percentage = 100*(current_time / total_time);
    var progress_bar = document.getElementById("playbackprogress");
    progress_bar.style.width = percentage.toString() + "%";
    document.getElementById("playbacktimercontainer").innerHTML = seconds_to_minutes(current_time) + " / " + seconds_to_minutes(total_time);
}

function update_player_play() {
    var icon = document.getElementById("play_button");
    icon.src = "/static/main/pause_button.png";
    onplaying = true;
    onpause = false;
}

function update_player_pause() {
    var icon = document.getElementById("play_button");
    icon.src = "/static/main/play_button.png";
    onplaying = false;
    onpause = true;
}

var random = true;
var track_id = 0;
var deck_position = 0;
var deck = []
var playlist_loaded = false;

var audio_player = document.createElement('AUDIO');
var onplaying = true;
var onpause = false;

audio_player.id = "audio_player";
audio_player.addEventListener('ended', get_next_song_decision);
audio_player.addEventListener('timeupdate', time_update);
audio_player.addEventListener('playing', update_player_play);
audio_player.addEventListener('pause', update_player_pause);
audio_player.type = "audio/mpeg";
audio_player.autoplay = true;
audio_player.volume = document.getElementById("volume_slider").value/100;
volume = audio_player.volume;
updateSoundIcon();

function get_next_song_decision() {
    if(playlist_loaded) {
        get_next_song();
    } else {
        load_random_song();
    }
}

function toggle_play() {
    if(audio_player.paused) {
        audio_player.play()
    } else {
        audio_player.pause()
    }
}

var volume = 1.0;
var volume_on = true;
$("#volume_slider").on('input', 
    function() {
        audio_player.volume = this.value/100;
        volume = this.value/100;
        updateSoundIcon();
        if(volume_on == false) {
            volume_on = true;
        }
    });


function toggle_volume() {
    if(volume_on) {
        volume_on = false;
        var icon = document.getElementById("volume_icon");
        icon.src = "/static/main/volume_off.png";
        audio_player.volume = 0;
        document.getElementById("volume_slider").value = 0;
    } else {
        volume_on = true;
        audio_player.volume = volume;
        document.getElementById("volume_slider").value = volume*100;
        updateSoundIcon();
    }
}

function get_random_track_id() {
    var rows = $('tr.track-info', hoverTable);
    numrows = rows.length;
    randnum = Math.floor(Math.random() * numrows);
    var current_track = track_id;

    // Never play the same song twice
    if(numrows > 1) {
        while(randnum == current_track) {
            randnum = Math.floor(Math.random() * numrows);
        }
    }
    track_id = randnum;
}

function increment_track_id() {
    var rows = $('tr.track-info', hoverTable);
    numrows = rows.length;
    track_id += 1;
    track_id %= numrows;
}

function choose_song(id) {
    $.get(
    "fetch_track_info?songid="+id,
    function(data) {
        var title = data.title;
        var artist = data.artist;
        var album = data.album;
        var page_title = data.title;
        var songid = data.songid;
        $('#song-name').html(title);
        $('#song_id').html(songid);

        if(typeof artist !== "undefined") {
            $('#artist-name').html(data.artist);
            page_title += ' - ' + data.artist + ' | Music';
        } else {
            $('#artist-name').html("&nbsp;");
            page_title += " | Music";
        }
        if(typeof album !== "undefined") {
            $('#album-name').html(data.album);
        } else {
            $('#album-name').html("&nbsp;");
        }
        $('#page_title').html(page_title);

        audio_player.src = 'get_song?songid=' + id;
        document.getElementById("albumartwork").src = 'fetch_album_artwork?songid=' + id;
        document.getElementById("playbackprogress").style.width = "0%";
        document.getElementById("playbacktimercontainer").innerHTML = "0:00 / 0:00";
    });
}

function get_next_song() {
    // First, check if we need to play a song we went back from
    if(deck_position < deck.length-1) {
        deck_position += 1;
        choose_song(deck[deck_position]);
        return;
    }
    // Otherwise, default behavior
    // Frist, we only want up to 100 songs stored to avoid memory issues
    if(deck.length > 100) {
        deck = deck.shift;
    }
    if(random) {
        load_random_song(); 
        return;
    } else {
        if(deck.length > 0) {
            track_id = deck[deck.length - 1]
        }
    }
    var next_track_id = get_next_song_id(track_id);
    if(next_track_id == -1) {
        return load_random_song();
    }
    deck.push(next_track_id);
    deck_position = deck.length-1;
    choose_song(next_track_id);
}

function get_next_song_id(current_id) {
    var table = document.getElementById("hoverTable");
    for(var i=0, row; row = table.rows[i]; i++) {
        if(parseInt(row.id) == parseInt(current_id)) {
            // Row 0 is the header, skip that.
            if(((i + 1) % table.rows.length) == 0)
            {
                return parseInt(table.rows[1].id);
            }
            var next_row = table.rows[(i+1) % table.rows.length];
            return (parseInt(next_row.id))
        }
    }
    console.log("Current track not found...");
    return -1;
}

function get_prev_song() {
    if(deck_position > 0) {
        deck_position -= 1;
    }
    choose_song(deck[deck_position]);
}

function resize_album_artwork() {
    var album_artwork = document.getElementById("albumartwork");
    var style = window.getComputedStyle(album_artwork);
    var width = album_artwork.offsetWidth - parseFloat(style.paddingLeft) - parseFloat(style.paddingRight) - parseFloat(style.marginLeft) - parseFloat(style.marginRight) - parseFloat(style.borderLeft) - parseFloat(style.borderRight);
    album_artwork.style.height = parseFloat(width) + "px";
}

function share_song() {
    var url = window.location.protocol;
    url += "//";
    url += window.location.hostname;
    url += "/?songid=";
    var mysongid = document.getElementById("song_id").textContent;
    url += mysongid;
    if(window.clipboardData && window.clipboardData.setData) {
        return clipboardData.setData("Text", url);
    } else if(document.queryCommandSupported && document.queryCommandSupported("copy")) {
        var textarea = document.createElement("textarea");
        textarea.textContent = url;
        textarea.style.position = "fixed";
        document.body.appendChild(textarea);
        textarea.select();
        try {
            document.execCommand("copy");
            alert("Link copied to clipboard!");
            return;
        } catch (ex) {
            console.warn("Copy to clipboard failed.", ex);
            window.prompt("Copy to clipboard: Ctrl+C or Cmd+C, Enter", text);
            return false;
        } finally {
            document.body.removeChild(textarea);
        }
    }
}

function random_song() {
    get_random_track_id();
    var rows = $('tr.track-info', hoverTable);
    var next_track_id = parseInt(rows[track_id].id);

    choose_song(next_track_id);
}

function toggle_shuffle() {
    var shuffle_icon = document.getElementById("shufflebutton");
    if(random) {
        random = false;
        shuffle_icon.classList.remove("shuffle-button-on");
        shuffle_icon.classList.add("shuffle-button-off");
    } else {
        random = true;
        shuffle_icon.classList.add("shuffle-button-on");
        shuffle_icon.classList.remove("shuffle-button-off");
    }
}

function listFilter() {
    var punctRE = /[\u2000-\u206F\u2E00-\u2E7F\\'!"#$%&()*+,\-.\/:;<=>?@\[\]^_`{|}~]/g;
    var spaceRE = /\s+/g;
    var substring = document.getElementById('search_bar').value.toLowerCase();
    substring = substring.replace(punctRE, '').replace(spaceRE, ' ');
    var table = document.getElementById('hoverTable');
    for(var i=1;i<table.rows.length;i++) {
        var title = table.rows[i].cells[0].textContent.toLowerCase().replace(punctRE, '').replace(spaceRE, ' ');
        var artist = table.rows[i].cells[1].textContent.toLowerCase().replace(punctRE, '').replace(spaceRE, ' ');
        var album = table.rows[i].cells[2].textContent.toLowerCase().replace(punctRE, '').replace(spaceRE, ' ');
        if( !title.includes(substring) &&
            !artist.includes(substring) &&
            !album.includes(substring)) {
            table.rows[i].style.display = 'none';
        } else {
            table.rows[i].style.display = '';
        }

    }
}

function downloadFile(uri, name) {
    var link = document.createElement("a");
    link.download = name;
    link.href = uri;
    document.body.appendChild(link);
    link.click();
    link.remove();
}

// Thank you sitepoint.com
// $.urlParam('parameter_name') returns parameter value
$.urlParam = function(name) {
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
    if(results == null) {
        return null;
    } else {
        return results[1] || 0;
    }
}

function load_random_song() {
    var playlist_id = $.urlParam('playlist_id');
    var url_parameters = "";
    if(playlist_id != null) {
        url_parameters += "?playlist_id=" + playlist_id;
    }
    if((deck.length > 1) && (deck_position < deck.length-1)) {
        deck_position += 1;
        choose_song(deck[deck_position]);
    } else {
        $.get(
        "get_random_song" + url_parameters,
        function(data) {
            var title = data.title;
            var artist = data.artist;
            var album = data.album;
            var page_title = data.title;
            var songid = data.songid;
            $('#song-name').html(title);
            $('#song_id').html(songid);

            if(typeof artist !== "undefined") {
                $('#artist-name').html(data.artist);
                page_title += ' - ' + data.artist + ' | Music';
            } else {
                $('#artist-name').html("&nbsp;");
                page_title += " | Music";
            }
            if(typeof album !== "undefined") {
                $('#album-name').html(data.album);
            } else {
                $('#album-name').html("&nbsp;");
            }
            $('#page_title').html(page_title);

            audio_player.src = data.src;
            document.getElementById("albumartwork").src = 'fetch_album_artwork?songid=' + songid;
            document.getElementById("playbackprogress").style.width = "0%";
            document.getElementById("playbacktimercontainer").innerHTML = "0:00 / 0:00";


            if(deck.length > 100) {
                deck = deck.shift;
            }

            deck.push(songid);
            deck_position = deck.length-1;
            track_id = data.songid;
        });
    }
}

// Either play the selected song, or choose a random one
if($.urlParam('songid') != null) {
    deck.push($.urlParam('songid'));
    choose_song($.urlParam('songid'));
} else { // choose a random song
    load_random_song();
}

resize_album_artwork();
$(window).resize(resize_album_artwork);

$("a.logoutlink").click(function() {
    window.location.href = "logout";
});

$("#playbackcontainer").click(function(e) {
    var percentage = e.offsetX/$(this).width();
    var time_to_set = parseInt(percentage*audio_player.duration);
    audio_player.currentTime = time_to_set;
});

$("#search_bar").keyup(listFilter);
$("#shufflebutton").click(toggle_shuffle);
$("#sharebutton").click(share_song);
$("#previous_button").click(get_prev_song);
$("#play_button").click(toggle_play);
$("#next_button").click(get_next_song_decision);
$("#downloadbutton").click(function() {
    var src = audio_player.src;
    var name = document.getElementById("song-name").innerHTML;
    name = name.split('.').join('');
    downloadFile(src, name);
});

function load_all_songs() {
    $.get(
        "get_playlist_songs",
        function(data) {
            var content_div = document.getElementById('playlist-content');
            var loader_div = document.getElementById('loader-container');
            content_div.removeChild(loader_div);
            content_div.innerHTML = data;
            playlist_loaded = true;
            set_song_select_function();
        });
}

function load_playlist_by_id(id) {
    $.get(
        "get_playlist_songs?playlist_id=" + id,
        function(data) {
            var content_div = document.getElementById('playlist-content');
            var loader_div = document.getElementById('loader-container');
            content_div.removeChild(loader_div);
            content_div.innerHTML = data;
            playlist_loaded = true;
            set_song_select_function();
        });
}

function load_playlist() {
    var param = new RegExp('[\?&]' + "playlist_id" + '=([^&#]*)').exec(window.location.href);
    if(param == null) {
        load_all_songs();
    } else {
        load_playlist_by_id(param[1] || 0);
    }
}

function set_song_select_function() {
    $("tr.track-info").click(function() {
        var rows = $('tr.track-info', hoverTable);
        while(deck.length > deck_position + 1) {
            deck.pop();
        }
        if(deck.length > 100) {
            deck = deck.shift;
        }
        deck.push(this.id);
        deck_position = deck.length-1;
        choose_song(this.id);
        track_id = this.id;
    });
}

load_playlist();
