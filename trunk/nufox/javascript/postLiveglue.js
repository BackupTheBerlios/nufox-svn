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

var TreeSelectionSet = function(treeid, itemid) {
    var tree = document.getElementById(treeid);
    var item = document.getElementById(itemid);
    tree.view.selection.select(tree.view.getIndexOfItem(item));
}

var TreeSelectionClear = function(treeid) {
    var tree = document.getElementById(treeid);
    tree.view.selection.clearSelection();
}

var TreeCheckTwistForToggle = function(tree, event) {
    var row = {}, column = {}, part = {};
    var boxobject = tree.boxObject;
    boxobject.QueryInterface(Components.interfaces.nsITreeBoxObject);
    boxobject.getCellAt(event.clientX, event.clientY, row, column, part);
    if (part.value=='twisty') {
        var item = tree.view.getItemAtIndex(row.value);
        server.handle('dummy', 'ontwist', tree.id, item.id);
    }
}
