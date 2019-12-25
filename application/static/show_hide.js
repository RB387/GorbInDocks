function show_hide(elements) {
    for(var i = 0; i < elements.length; i++){
        var x = document.getElementById(elements[i]);
        if (x.style.display === "none") {
        x.style.display = "block";
        } else {
        x.style.display = "none";
        }
    }
}
                        