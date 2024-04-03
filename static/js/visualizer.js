var myChart = document.getElementsByClassName("myChart")[0].getContext("2d");

var gradient = myChart.createLinearGradient(0, 0, 800, 0); //x0, y0, x1, y1
gradient.addColorStop(0, "#A48CED");
gradient.addColorStop(1, "#4B13EC");

var SRSCharte = new Chart(myChart, {
  type: "line",

});
