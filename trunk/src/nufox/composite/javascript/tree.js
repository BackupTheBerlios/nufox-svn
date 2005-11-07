// Tree widget functions.


var TreeGetSelected = function(id) {
    var tree = document.getElementById(id);
    var start = new Object();
    var end = new Object();
    var numRanges = tree.view.selection.getRangeCount();
    var ret = new Array();
    for (var t=0; t<numRanges; t++) {
        tree.view.selection.getRangeAt(t,start,end);
        for (var v=start.value; v<=end.value; v++) {
            if(v!=-1) ret[ret.length] = tree.view.getItemAtIndex(v).id;
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


var NestedTreeLoadSubTree = function(tree, event, shouldBeTwist) {
    var row = {}, column = {}, part = {};
    var boxobject = tree.boxObject;
    boxobject.QueryInterface(Components.interfaces.nsITreeBoxObject);
    boxobject.getCellAt(event.clientX, event.clientY, row, column, part);
    if (((part.value=='twisty') && shouldBeTwist) ||
            ((part.value!='twisty') && !shouldBeTwist)) {
        var item = tree.view.getItemAtIndex(row.value);
        if(!item.loaded){
            server.handle('dummy', 'onloadsubtree', tree.id, item.id);
            item.loaded = true;
        }
    }
}


var FlatTreeSetView = function(treeid, rowCount) {
    var tree = document.getElementById(treeid);
    var view = {
        rowCount: rowCount,
        getCellText: function(row, column) {
            // XXX: call remote method on widget here.
        },
        setTree: function(treebox){ this.treebox = treebox; },
        isContainer: function(row){ return false; },
        isSeparator: function(row){ return false; },
        isSorted: function(row){ return false; },
        getLevel: function(row){ return 0; },
        getImageSrc: function(row,col){ return null; },
        getRowProperties: function(row,props){},
        getCellProperties: function(row,col,props){},
        getColumnProperties: function(colid,col,props){}
    };
    tree.view = view;
}