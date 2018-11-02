function load_all_songs() {
    $.get(
        "get_playlist_songs",
        function(data) {
            var content_div = document.getElementById('playlist-content');
            var loader_div = document.getElementById('loader-container');
            content_div.removeChild(loader_div);
            content_div.innerHTML = data;
            playlist_loaded = true;
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

load_playlist();
