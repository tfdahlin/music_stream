var rc_song_id = 0;

function mouseX(evt) {
    if (evt.pageX) {
        return evt.pageX;
    } else if (evt.clientX) {
       return evt.clientX + (document.documentElement.scrollLeft ?
           document.documentElement.scrollLeft :
           document.body.scrollLeft);
    } else {
        return null;
    }
}

function mouseY(evt) {
    if (evt.pageY) {
        return evt.pageY;
    } else if (evt.clientY) {
       return evt.clientY + (document.documentElement.scrollTop ?
       document.documentElement.scrollTop :
       document.body.scrollTop);
    } else {
        return null;
    }
}

if (document.addEventListener) { // IE >= 9; other browsers
    document.addEventListener('contextmenu', function(e) {
        //alert("You've tried to open context menu"); //here you draw your own menu
        if($(e.target).hasClass("track-info")) {
            e.preventDefault();

            document.getElementById("rmenu").className = "show";  
            document.getElementById("rmenu").style.top =  mouseY(e) + 'px';
            document.getElementById("rmenu").style.left = mouseX(e) + 'px';
            song_id = e.target.id;
            $(document).bind("click", function(event) {
                document.getElementById("rmenu").className = "hide";
                $(document).unbind("click", function(event) {
                });
            });
        }
    }, false);
}

function add_song_to_playlist(playlist_id, rc_song_id) {
    $.get(
    "/add_to_playlist?playlist_id=" + playlist_id + "&songid=" + rc_song_id);
}

function remove_song_from_playlist(playlist_id, rc_song_id) {
    $.get(
    "/remove_from_playlist?playlist_id=" + playlist_id + "&songid=" + rc_song_id, function() {
        location.reload();
    });
}

function request_playlist_name() {
    var new_playlist_name = prompt("Create a new playlist", "Playlist name");

    if(new_playlist_name == null || new_playlist_name == "") {
    } else {
        // TODO: Report playlist name taken if it is.
        $.get("create_playlist?playlist_name=" + new_playlist_name, function() {
            location.reload() });
    }
}

function go_to_playlist() {
    var decision = document.getElementById("playlistoptions");
    if(decision.value== "0")
    {
        var playlist_id = new RegExp('[\?&]' + "playlist_id" + '=([^&#]*)').exec(window.location.href);
        if(playlist_id != null) {
            window.location.href = "/";
        } 
    } else {
        window.location.href = "/?playlist_id=" + decision.options[decision.selectedIndex].value;
    }
}

$("td.playlist").click(function() {
    var playlist = this.id;
    add_song_to_playlist(playlist, rc_song_id);
});

$("td.removetrack").click(function() {
    var playlist = this.id;
    remove_song_from_playlist(playlist, rc_song_id);
});

$("#new_playlist_button").click(request_playlist_name);

$("#go_to_playlist_button").click(go_to_playlist);
