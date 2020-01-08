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
function openNav() {
    document.getElementById("mySidenav").style.width = "250px";
}

function closeNav() {
    document.getElementById("mySidenav").style.width = "0";
}
function change() {
  if (document.getElementById("p2").style.display = "inline-block") {
    document.getElementById("p2").style.display = "none";
  }
}
