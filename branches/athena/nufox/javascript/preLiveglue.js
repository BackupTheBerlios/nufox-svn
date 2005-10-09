/* BEGIN Core functions for nufox */

var rCall = function(element, event) {
    var args = [];
    args.push("__"+element.id+"__"+event); //The event handler to call
    for (var i = 1; i < arguments.length; i++) {
        //Lets look for some special args like a__<id>__<attribute>
        if(arguments[i].split('__').length > 1) {
            var bits = arguments[i].split('__');
            args.push(self.getElementById(bits[1]).getAttribute(bits[2]))
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
}

var remove = function(parentId, childId) {
    /* Remove node with 'childId' from node with 'parentId'. */
    document.getElementById(parentId).removeChild(
        document.getElementById(childId));
}

var removeNodes = function(parentId, nodesToRemove) {
    for(n in nodesToRemove) {
        remove(parentId, n);
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

var getAttr = function(id, attr) {
    var node = document.getElementById(id);
    if(node[attr]==undefined) return node.getAttribute(attr);
    return node[attr];
}

var err = function(error) {
    alert("Error: " + error);
}
/* END Core functions for nufox */




