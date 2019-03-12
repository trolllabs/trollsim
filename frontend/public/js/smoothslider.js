function sendSliderValue(id) {
	return function (value, meta) {
			if (meta.triggeredByUser)
				sock.send(id + ' ' + value);
		}
}

$(window).ready(function() {
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

