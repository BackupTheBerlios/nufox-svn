
var handleDisconnect = function() {
    /* I get called when the server drops the connection */
    //alert("Your connection to the nufox server has been closed.");
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

/* Tree widget funcs */

var TreeGetSelected = function(id) {
    var tree = document.getElementById(id);
    var start = new Object();
    var end = new Object();
    var numRanges = tree.view.selection.getRangeCount();
    var ret = new Array();
    for (var t=0; t<numRanges; t++) {
        tree.view.selection.getRangeAt(t,start,end);
        for (var v=start.value; v<=end.value; v++) {
            ret[ret.length] = tree.view.getItemAtIndex(v).id;
        }
    }
    return ret;
}
