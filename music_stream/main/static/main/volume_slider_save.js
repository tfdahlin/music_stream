$("#volume_slider").on('mouseup', function () {
    $.get(
    "update_volume?volume="+(this.value/100));
});
