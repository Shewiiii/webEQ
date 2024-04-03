var hauteur = window.outerHeight;
var hauteurelement = document.getElementById("pageform").offsetHeight;
var padding = (hauteur - hauteurelement) / 4;

document
  .getElementById("pageform")
  .setAttribute("style", "padding-top:" + padding + "px;margin: 0;");
