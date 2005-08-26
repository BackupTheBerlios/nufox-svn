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

var TreeSetSelected = function(treeid, itemid) {
    var tree = document.getElementById(treeid);
    var item = document.getElementById(itemid);
    tree.view.selection.select(tree.view.getIndexOfItem(item));
}

function nsTreeView() {}
nsTreeView.prototype = {

    QueryInterface : function QueryInterface(aIID) {
        if (Components.interfaces.nsIClassInfo.equals(aIID))
            return nsTreeView.prototype;
        if (Components.interfaces.nsITreeView.equals(aIID) ||
            Components.interfaces.nsISupportsWeakReference.equals(aIID) ||
            Components.interfaces.nsISupports.equals(aIID))
                return this;
        throw 0x80004002; // Components.results.NS_NOINTERFACE;
    },

    getInterfaces: function getInterfaces(count) {
        count.value = 4;
        return [Components.interfaces.nsITreeView,
                Components.interfaces.nsIClassInfo,
                Components.interfaces.nsISupportsWeakReference,
                Components.interfaces.nsISupports];
    },

    get classDescription() { return "nsTreeView"; },
    get flags() { return Components.interfaces.nsIClassInfo.DOM_OBJECT; },

    childData : {
        tmp: ["file1", "file2"],
        usr: [{"bin": ["ls", "awk"], "lib": ["libcore1", "libstd2.3"]}]
    },

    visibleData : [
        ["tmp", true, false],
        ["usr", true, false]
    ],

    treeBox: null,
    selection: null,

    get rowCount()                     { return this.visibleData.length; },
    setTree: function(treeBox)         { this.treeBox = treeBox; },
    getCellText: function(idx, column) { return this.visibleData[idx][0]; },
    isContainer: function(idx)         { return this.visibleData[idx][1]; },
    isContainerOpen: function(idx)     { return this.visibleData[idx][2]; },
    isContainerEmpty: function(idx)    { return false; },
    isSeparator: function(idx)         { return false; },
    isSorted: function()               { return false; },
    isEditable: function(idx, column)  { return false; },

    getParentIndex: function(idx) {
        if (this.isContainer(idx)) return -1;
        for (var t = idx - 1; t >= 0 ; t--) {
            if (this.isContainer(t)) return t;
        }
    },

  getLevel: function(idx) {
    if (this.isContainer(idx)) return 0;
    return 1;
  },

  hasNextSibling: function(idx, after) {
    var thisLevel = this.getLevel(idx);
    for (var t = idx + 1; t < this.visibleData.length; t++) {
      var nextLevel = this.getLevel(t)
      if (nextLevel == thisLevel) return true;
      else if (nextLevel < thisLevel) return false;
    }
  },

  toggleOpenState: function(idx) {
    var item = this.visibleData[idx];
    if (!item[1]) return;

    if (item[2]) {
      item[2] = false;

      var thisLevel = this.getLevel(idx);
      var deletecount = 0;
      for (var t = idx + 1; t < this.visibleData.length; t++) {
        if (this.getLevel(t) > thisLevel) deletecount++;
        else break;
      }
      if (deletecount) {
        this.visibleData.splice(idx + 1, deletecount);
        this.treeBox.rowCountChanged(idx + 1, -deletecount);
      }
    }
    else {
      item[2] = true;

      var label = this.visibleData[idx][0];
      var toinsert = this.childData[label];
      for (var i = 0; i < toinsert.length; i++) {
        this.visibleData.splice(idx + i + 1, 0, [toinsert[i], false]);
      }
      this.treeBox.rowCountChanged(idx + 1, toinsert.length);
    }
  },

    getImageSrc: function(idx, column) {},
    getProgressMode : function(idx,column) {},
    getCellValue: function(idx, column) {},
    cycleHeader: function(col, elem) {},
    selectionChanged: function() {},
    cycleCell: function(idx, column) {},
    performAction: function(action) {},
    performActionOnCell: function(action, index, column) {},
    getRowProperties: function(idx, column, prop) {},
    getCellProperties: function(idx, column, prop) {},
    getColumnProperties: function(column, element, prop) {},
}
