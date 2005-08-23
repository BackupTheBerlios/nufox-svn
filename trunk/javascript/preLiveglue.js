/* BEGIN Core functions for nufox */

var addNode = function(parentId, element, newId, attrs) {
    w = document.createElement(element);
    w.setAttribute('id', newId);
    for(key in attrs) {
        w.setAttribute(key, attrs[key]);
    }
    document.getElementById(parentId).appendChild(w);
}

var remove = function(parentId, childId) {
    /* Remove node with 'childId' from node with 'parentId'. */
    document.getElementById(parentId).removeChild(
        document.getElementById(childId));
}

var setAttr = function(id, attr, value) {
    /* Set attribute 'attr' on node with 'id' to 'value'. */ 
    document.getElementById(id).setAttribute(attr, value);
}

/* END Core functions for nufox */




