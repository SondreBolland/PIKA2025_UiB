function updateNav() {
    for (var i = 0; i < document.navCards.length; i++) {
	if (i == document.navCurr) {
	    document.navCards[i].style.display = "block";
	} else {
	    document.navCards[i].style.display = "none";
	}
    }

    var prev = document.getElementById("navPrev");
    prev.disabled = document.navCurr == 0;
    prev.blur();
    var next = document.getElementById("navNext");
    next.disabled = document.navCurr == document.navCards.length - 1;
    next.blur();
}

function navPrev() {
    document.navCurr--;
    updateNav();
}

function navNext() {
    document.navCurr++;
    updateNav();
}

window.onload = function() {
    document.navCards = document.getElementsByName("card");
    document.navCurr = 0;

    updateNav();
}
