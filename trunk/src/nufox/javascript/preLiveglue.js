// Core functions for nufox, required to be loaded before liveglue
// functions are loaded.


var rCall = function(element, event) {

    var args = [];
    args.push("__"+element.id+"__"+event); //The event handler to call

    for (var i = 1; i < arguments.length; i++) {

        // Lets look for some special args
        var a = arguments[i];
        if(typeof(a) == typeof([]) && a.length > 1) {
            switch(a[0]) {
                case '_a':
                    var el = document.getElementById(a[1]);
                    if(el[a[2]]==undefined) args.push(el.getAttribute(a[2]));
                    else args.push(el[a[2]]);
                    break;
                case '_m':
                    var el = document.getElementById(a[1]);
                    args.push(el[a[2]].apply(el, a[3]));
                    break;
                case '_f':
                    args.push(window[a[1]].apply(window, a[2]));
                    break;
                default:
                    args.push(arguments[i]);
            }
        } else {
            args.push(arguments[i]);
        }
    }
    d = server.callRemote.apply(server, args);
    d.addErrback(err);
    return d;
}


var addNode = function(parentId, element, attrs) {
    var w = document.createElement(element);
    for(var key in attrs) {
        w.setAttribute(key, attrs[key]);
    }
    document.getElementById(parentId).appendChild(w);
}


var appendNodes = function(newNodesList) {
    for(var n in newNodesList) {
        var node = newNodesList[n];
        addNode(node[0], node[1], node[2]);
    }
    return true;
}


var remove = function(parentId, childId) {
    /* Remove node with 'childId' from node with 'parentId'. */
    document.getElementById(parentId).removeChild(
        document.getElementById(childId));
}


var removeNodes = function(parentId, nodesToRemove) {
    for(var n in nodesToRemove) {
        remove(parentId, nodesToRemove[n]);
    }
}


var setAttr = function(id, attr, value) {
    /* Set attribute 'attr' on node with 'id' to 'value'.

    This might seem a bit odd but some xul widgets only
    support one or the other method of setting attrs.. */
    document.getElementById(id).setAttribute(attr, value);
    document.getElementById(id)[attr] = value;
    return true;
}


var callMethod = function(id, method, args) {
    var node = document.getElementById(id);
    return node.getAttribute(method).apply(node, args);
}


var widgetMethod = function(id, methodName /*, ... */) {
    var args = [id, methodName];
    for (var i = 2; i < arguments.length; i++) {
        args.push(arguments[i]);
    }
    d = server.callRemote.apply(server, args);
    d.addErrback(err);
    return d;
}


var getAttr = function(id, attr) {
    var node = document.getElementById(id);
    if(node[attr]==undefined) return node.getAttribute(attr);
    return node[attr];
}


var err = function(error) {
    alert("Error: " + error);
}


var newWindow = function(url) {
    //window.open(url, null, 'width=300, height=300');
    window.open(url, null);
}


var setWindowTitle = function(title) {
    document.title = title;
}


var resizeWindow = function(width, height) {
    window.resizeTo(width, height);
}
