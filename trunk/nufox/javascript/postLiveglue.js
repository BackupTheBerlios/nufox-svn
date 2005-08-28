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


/*
    XXX - this sort of stuff should be in some sort of core
    framework.  preferably for livepage i guess.
 */
function raiseEvent( elm, evType ) {
    if ( elm.dispatchEvent ) {
        var oEvent = document.createEvent("Events");
        oEvent.initEvent( evType, true, true);
        elm.dispatchEvent( oEvent );
    } else {
        elm.fireEvent( "on"+evType );
    }
}

var ned = function(tree, event) {
    var row = {}, column = {}, part = {};
    var boxobject = tree.boxObject;
    boxobject.QueryInterface(Components.interfaces.nsITreeBoxObject);
    boxobject.getCellAt(event.clientX, event.clientY, row, column, part);
    if (part.value=='twisty') {
        raiseEvent(tree, 'ontwist');
    }
}

/*
    lifted from: http://xulplanet.com/tutorials/xulqa/q_treebview.html
 */
function nsTreeView() {}
nsTreeView.prototype = {
    /* debugging */
    get wrappedJSObject() { return this; },
    /* nsISupports */
    QueryInterface : function QueryInterface(aIID) {
        if (Components.interfaces.nsIClassInfo.equals(aIID))
            return nsTreeView.prototype;
        if (Components.interfaces.nsITreeView.equals(aIID) ||
            Components.interfaces.nsISupportsWeakReference.equals(aIID) ||
            Components.interfaces.nsISupports.equals(aIID))
                return this;
            throw 0x80004002; // Components.results.NS_NOINTERFACE;
    },
    /* nsIClassInfo */
    getInterfaces: function getInterfaces(count) {
        count.value = 4;
        return [Components.interfaces.nsITreeView,
                Components.interfaces.nsIClassInfo,
                Components.interfaces.nsISupportsWeakReference,
                Components.interfaces.nsISupports];
    },
    getHelperForLanguage: function getHelperForLanguage(language) { return null; },
    get contractID() { return null; },
    get classDescription() { return "nsTreeView"; },
    get classID() { return null; },
    get implementationLanguage() { return Components.interfaces.nsIProgrammimgLanguage.JAVASCRIPT; },
    get flags() { return Components.interfaces.nsIClassInfo.DOM_OBJECT; },
    /* nsITreeView */
    get rowCount() { return this._subtreeItems.length; },
    selection: null,
    getRowProperties: function getRowProperties(index, prop) { },
    getCellProperties: function getCellProperties(index, column, prop) { },
    getColumnProperties: function getColumnProperties(column, elem, prop) { },
    isContainer: function isContainer(index) {
        if (index in this._subtreeItems)
            return this._subtreeItems[index]._isContainer;
        throw 0x8000FFFF; // Components.results.NS_ERROR_UNEXPECTED;
    },
    isContainerOpen: function isContainerOpen(index) { return this._subtreeItems[index]._open; },
    isContainerEmpty: function isContainerEmpty(index) { return this._subtreeItems[index]._isContainerEmpty; },
    isSeparator: function isSeparator(index) { return false; },
    isSorted: function isSorted() { return false; },
    // d&d not implemented yet!
    canDropOn: function canDropOn(index) { return false; },
    canDropBeforeAfter: function canDropBeforeAfter(index, before) { return false; },
    drop: function drop(index, orientation) { },
    getParentIndex: function getParentIndex(index) {
        return this.getIndexOfItem(this._subtreeItems[index]._parentItem);
    },
    hasNextSibling: function hasNextSibling(index, after) { return this._subtreeItems[index]._hasNext; },
    getLevel: function getLevel(index) {
        if (index in this._subtreeItems) {
            var level = 0;
            for (var item = this._subtreeItems[index]; item._parentItem != this; ++level)
                item = item._parentItem;
            return level;
        }
        throw 0x8000FFFF; // Components.results.NS_ERROR_UNEXPECTED;
    },
  getImageSrc: function getImageSrc(index, column) { },
  getProgressMode : function getProgressMode(index,column) { },
  getCellValue: function getCellValue(index, column) { },
  getCellText: function getCellText(index, column) {
    if (index in this._subtreeItems)
      return this._subtreeItems[index][column];
    throw 0x8000FFFF; // Components.results.NS_ERROR_UNEXPECTED;
  },
  setTree: function setTree(treeBox) { this._treeBox = treeBox; if (!treeBox) this.selection = null; },
  cycleHeader: function cycleHeader(col, elem) { },
  selectionChanged: function selectionChanged() { },
  cycleCell: function cycleCell(index, column) { },
  isEditable: function isEditable(index, column) { return false; },
  performAction: function performAction(action) { },
  performActionOnCell: function performActionOnCell(action, index, column) { },
  toggleOpenState: function toggleOpenState(index) { this._subtreeItems[index].toggleState(); },
  /* utility methods */
  getChildCount: function getChildCount() { return this._childItems.length; },
  getIndexOfItem: function getIndexOfItem(item) {
    if (!item)
      throw 0x80004003; // Components.results.NS_ERROR_NULL_POINTER;
    var index = -1;
    while (item != this) {
      var parent = item._parentItem;
      if (!parent)
        throw 0x80004005; // Components.results.NS_ERROR_FAILURE;
      for (var i = 0; (tmp = parent._childItems[i]) != item; ++i)
        if (tmp._open)
          index += tmp._subtreeItems.length;
      index += i + 1;
      item = parent;
    }
    return index;
  },
  getIndexOfChild: function getIndexOfChild(item) {
    if (!item)
      throw 0x80004003; // Components.results.NS_ERROR_NULL_POINTER;
    if (item._parentItem != this)
      throw 0x80004005; // Components.results.NS_ERROR_FAILURE;
    for (var i = 0; i < this._childItems.length; ++i)
      if (this._childItems.length[i] == item)
        return i;
    throw 0x80004005; // Components.results.NS_ERROR_FAILURE;
  },
  getItemAtIndex: function getItemAtIndex(index) {
    index = parseInt(index) || 0;
    if (index < 0 || index >= this._subtreeItems.length)
      throw 0x80004005; // Components.results.NS_ERROR_FAILURE;
    return this._subtreeItems[index];
  },
  getChildAtIndex: function getChildAtIndex(index) {
    index = parseInt(index) || 0;
    if (index < 0 || index >= this._childItems.length)
      throw 0x80004005; // Components.results.NS_ERROR_FAILURE;
    return this._childItems[index];
  },
  selectItem: function selectItem(item) {
    for (var parent = item.parentItem(); parent != this; parent = parent.parentItem())
      if (!parent)
        throw 0x80004005; // Components.results.NS_ERROR_FAILURE;
      else if (!parent.isOpen())
        parent.toggleState();
    var index = this.getIndexOfItem(item);
    this.selection.select(index);
    this._treeBox.ensureRowIsVisible(index);
  },
  invalidateRow: function invalidate() {
    var offset = -1;
    var parent;
    for (var item = this; parent = item._parentItem; item = parent) {
      offset += item._getOffset();
      if (parent._treeBox)
        parent._treeBox.invalidateRow(offset);
      if (!parent._open)
        break;
    }
  },
  invalidatePrimaryCell: function invalidatePrimaryCell() {
    var offset = -1;
    var parent;
    for (var item = this; parent = item._parentItem; item = parent) {
      offset += item._getOffset();
      if (parent._treeBox)
        parent._treeBox.invalidatePrimaryCell(offset);
      if (!parent._open)
        break;
    }
  },
  invalidateCell: function invalidateCell(column) {
    var offset = -1;
    var parent;
    for (var item = this; parent = item._parentItem; item = parent) {
      offset += item._getOffset();
      if (parent._treeBox)
        parent._treeBox.invalidateCell(offset);
      if (!parent._open)
        break;
    }
  },

    toggleState: function toggleState() {

        if(!this._isContainerLoaded) {
            server.handle('dummy', 'loadChildren', 'myTree', this._parentItem.getIndexOfItem(this))
            this.appendItem(new Item("fred1", true, true))
            this.appendItem(new Item("fred2", true, true))
            this._isContainerLoaded = true;
        }

        this._open = !this._open;
        if (this._subtreeItems.length && this._parentItem) {
            if (this._open) {
                this._parentItem._itemExpanded(this._getOffset(), this._subtreeItems);
            } else {
                this._parentItem._itemCollapsed(this._getOffset(), this._subtreeItems.length);
            }
        }
    },

  removeItem: function removeItem(item) {
    if (!item)
      throw 0x80004003; // Components.results.NS_ERROR_NULL_POINTER;
    if (item._parentItem != this)
      throw 0x80004005; // Components.results.NS_ERROR_FAILURE;
    var change = 1;
    if (item._open)
      change += item._subtreeItems.length;
    var offset = 0;
    var tmp;
    for (var i = 0; (tmp = this._childItems[i]) != item; ++i)
      if (tmp._open)
        offset += tmp._subtreeItems.length;
    offset += i;
    this._childItems.splice(i, 1);
    if (i)
      this._childItems[i - 1]._hasNext = item._hasNext;
    item._hasNext = false;
    this._subtreeItems.splice(offset, change);
    if (this._treeBox)
      this._treeBox.rowCountChanged(offset, -change);
    if (this._parentItem)
      this._parentItem._itemCollapsed(offset + this._getOffset(),
        this._open ? change : 0, this._childItems.length);
    item._parentItem = null;
  },
  appendItem: function appendItem(item) {
    this.insertItem(item, this._childItems.length);
  },
  insertItem: function insertItem(item, index) {
    if (!item)
      throw 0x80004003; // Components.results.NS_ERROR_NULL_POINTER;
    var length = this._childItems.length;
    index = parseInt(index) || 0;
    if (index < 0 || index > length)
      throw 0x80004005; // Components.results.NS_ERROR_FAILURE;
    if (item._parentItem)
      item._parentItem.removeItem(item);
    item._parentItem = this;
    var newItems = [item];
    var offset = index;
    if (!length)
      this._childItems = newItems;
    else {
      this._childItems.splice(index, 0, item);
      if (index == length) {
        this._childItems[length - 1]._hasNext = true;
        offset = this._subtreeItems.length;
      } else {
        item._hasNext = true;
        for (var i = 0; i < index; ++i)
          if (this._childItems[i]._open)
            offset += this._childItems[i]._subtreeItems.length;
      }
    }
    if (item._open)
      newItems = newItems.concat(item._subtreeItems);
    this._subtreeItems = this._subtreeItems.splice(0, offset).concat(newItems).
                           concat(this._subtreeItems);
    if (this._treeBox)
      this._treeBox.rowCountChanged(offset, newItems.length);
    if (this._parentItem && (this._open || !length))
      this._parentItem._itemExpanded(offset + this._getOffset(), this._open ? newItems : [], length);
  },
  parentItem: function parentItem() {
    return this._parentItem;
  },
  isOpen: function isOpen() {
    return this._open;
  },
  /* helper methods */
  _itemExpanded: function _itemExpanded(offset, newItems, notwisty) {
    this._subtreeItems = this._subtreeItems.splice(0, offset).concat(newItems).
                           concat(this._subtreeItems);
    if (this._treeBox) {
      this._treeBox.rowCountChanged(offset, newItems.length);
      if (offset && !notwisty)
        this._treeBox.invalidatePrimaryCell(offset - 1);
    }
    if (this._open && this._parentItem)
      this._parentItem._itemExpanded(offset + this._getOffset(), newItems);
  },
  _itemCollapsed: function _itemCollapsed(offset, change, notwisty) {
    this._subtreeItems.splice(offset, change);
    if (this._treeBox) {
      this._treeBox.rowCountChanged(offset, -change);
      if (offset && !notwisty)
        this._treeBox.invalidatePrimaryCell(offset - 1);
    }
    if (this._open && this._parentItem)
      this._parentItem._itemCollapsed(offset + this._getOffset(), change);
  },
  _getOffset: function _getOffset() {
    var offset = 1;
    var tmp;
    for (var i = 0; (tmp = this._parentItem._childItems[i]) != this; ++i)
      if (tmp._open)
        offset += tmp._subtreeItems.length;
    return offset + i;
  },

    /* default values */
    _parentItem: null,
    _hasNext: false,
    _childItems: [],
    _subtreeItems: [],
    _open: false,
    _treeBox: null,

    _isContainer: false,
    _isContainerEmpty: true,
    _isContainerLoaded: false

};

function _cbTreeLoadChildren(treeId, itemIndex) {
    var tree = document.getElementById(treeId);
    var view = tree.view;
    for(var x in view){
        alert(x);
    }
}

function Item(folder, isContainer, isContainerEmpty) {
  this.folder = folder;
  this._isContainer = isContainer;
  this._isContainerEmpty = isContainerEmpty;
}
Item.prototype = new nsTreeView();

function init() {
    var view = new nsTreeView();
    view.appendItem(new Item("tmp", true, false));
    view.appendItem(new Item("usr", true, false));
    document.getElementById("myTree").view = view;
}
