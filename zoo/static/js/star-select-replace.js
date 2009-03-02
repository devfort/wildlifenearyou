function selectReplacement(obj) {
	obj.className += ' replaced';
	var ul = document.createElement('ul');
	ul.className = 'selectReplacement';
	var opts = obj.options;
	for (var i=0; i<opts.length; i++) {
		var selectedOpt;
		if (opts[i].selected) {
			selectedOpt = i;
			break;
		} else {
			selectedOpt = 0;
		}
	}
	for (var i=0; i<opts.length; i++) {
		var li = document.createElement('li');
		var link = document.createElement('a');
		li.appendChild(link);
		li.className = opts[i].className;
		link.selIndex = opts[i].index;
		link.selectID = obj.id;
		link.setAttribute('href','#');
		link.onclick = function() {
			selectMe(this);
			return false;
		}
		if (i == selectedOpt) {
			ul.className = 'selectReplacement '+opts[i].className;
		}
		ul.appendChild(li);
	}
	obj.parentNode.insertBefore(ul,obj);
}
function selectMe(obj) {
	setVal(obj.selectID, obj.selIndex);
	var list = obj.parentNode.parentNode;
	list.className = 'selectReplacement '+obj.parentNode.className;
}
function setVal(objID, selIndex) {
	var obj = document.getElementById(objID);
	obj.selectedIndex = selIndex;
}

jQuery(document).ready(function() {
	if (document.getElementById('rating')) {
		selectReplacement(document.getElementById('rating'));
	}
});