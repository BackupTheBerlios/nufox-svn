// Player widget functions.


var PlayerPlay = function(id) {
    document.getElementById(id).DoPlay();
}


var PlayerPause = function(id) {
    alert(id);
    document.getElementById(id).DoPause();
}


var PlayerStop = function(id) {
    document.getElementById(id).DoStop();
}
