// script to past in the console to get the array of the active phones (https://crinacle.com/graphs/iems/graphtool/) 
for (const iem of document.getElementById('GraphTool').contentWindow.allPhones) {
  if (iem['active'] == true) {
		var average = [];
		var left = iem['channels'][0];
		var right = iem['channels'][1];

		for(i = 0; i < left.length; i++) {
			average.push([left[i][0],(left[i][1] + right[i][1]) / 2]);
    }
		var all = [average,iem['dispBrand']+ ' ' +iem['phone']];
    console.log(all);
  }
}
