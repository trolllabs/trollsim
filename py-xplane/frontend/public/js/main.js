	var series1 = new Array(10).fill(0);
	var series2 = new Array(10).fill(0);
	var series3 = new Array(10).fill(0);
	var series4 = new Array(10).fill(0);
	var labels = [];
	var linedata1 = { labels: labels, series: [series1] };
	//var linedata2 = { labels: labels, series: [series2] };
	//var linedata3 = { labels: labels, series: [series3] };
	//var linedata4 = { labels: labels, series: [series4] };
	var options = { high: 1.5, low: -1.0 };

	var chart1 = new Chartist.Line('#chart1', linedata1, options);
	//var chart2 = new Chartist.Line('#chart2', linedata2, options);
	//var chart3 = new Chartist.Line('#chart3', linedata3, options);
	//var chart4 = new Chartist.Line('#chart4', linedata4, options);
	const logger = document.getElementById('log');

	function printData(e) {
		logger.innerHTML = e.data + "\n";
	}

	function updateGraph(e) {
		data = e.data.trim().split(' ')
		series1.splice(0, 1);
		//series2.splice(0, 1);
		//series3.splice(0, 1);
		//series4.splice(0, 1);
		series1.push(data[0]);
		//series2.push(data[1]);
		//series3.push(data[2]);
		//series4.push(data[3]);
		chart1.update({series: [series1], labels: labels}, null, false);
		//chart2.update({series: [series2], labels: labels}, null, false);
		//chart3.update({series: [series3], labels: labels}, null, false);
		//chart4.update({series: [series4], labels: labels}, null, false);
	}

	sock.addEventListener('message', printData);
	sock.addEventListener('message', updateGraph);

	function sendMessage() {
		sock.send(document.getElementById('text').value);
	}


	function sendSliderValue(id) {
		return function (value, meta) {
			if (meta.triggeredByUser) {
				sock.send(id + ' ' + value);
			}
		}
	}

	$(document).ready(function() {
		$('#slider0').range({
			min: 0.0,
			max: 2,
			start: 1,
			step: 0.01,
			input: '#sliderinput0',
			onChange: sendSliderValue(0)
		});
		$('#slider1').range({
			min: 0.0,
			max: 2,
			start: 1,
			step: 0.01,
			input: '#sliderinput1',
			onChange: sendSliderValue(1)
		});
		$('#slider2').range({
			min: 0.0,
			max: 2,
			start: 1,
			step: 0.01,
			input: '#sliderinput2',
			onChange: sendSliderValue(2)
		});
		$('#slider3').range({
			min: 0.0,
			max: 2,
			start: 1,
			step: 0.01,
			input: '#sliderinput3',
			onChange: sendSliderValue(3)
		});

	});
