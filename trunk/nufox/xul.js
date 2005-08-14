
var handleDisconnect = function() {
    /* I get called when the server drops the connection */
    alert("Your connection to the nufox server has been closed.");
}
addDisconnectListener(handleDisconnect);

/* Player widget funcs */

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
