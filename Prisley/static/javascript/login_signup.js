
function checkInput(input, label){
	if (input.value.length > 0){
		document.getElementById(label).className = 'active';
	}
	else {
		document.getElementById(label).className = 'nonactive';
	}
}

function onFocus(label) {
    document.getElementById(label).className = 'active';
}

// to fix tab not resizing the text
$('.input-group>input').on('keyup', function (key) {
	if (key.which==9){
		var currentIndex = this.tabIndex;
		if (currentIndex > 4){
			console.log("Heyja");
			currentIndex = 0;
		}
		var tabAbles = document.getElementsByClassName("tabable");
		for (var i = 1; i < tabAbles.length; i++){
			if (tabAbles[i].tabIndex == currentIndex+1){
				// tabAbles[i].parentNode.lastChild.className="active";
				// console.log(tabAbles[i].parentNode.lastChild.className);
			}
		}
	}
});

function redirect(url) {
	window.location = url;
}

