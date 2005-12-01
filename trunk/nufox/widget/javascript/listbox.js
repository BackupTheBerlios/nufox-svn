// ListBox widget functions.


var ListBoxGetSelectedId = function(listBoxId) {
    var listBox = document.getElementById(listBoxId);
    var selectedItem = listBox.getSelectedItem(0);
    return selectedItem.id;
}
