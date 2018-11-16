const sock = new WebSocket('ws://' + window.location.hostname + ':8000');
const logger = document.getElementById('log');

sock.addEventListener('open', function(event) {
});

sock.addEventListener('message', function(event) {
	logger.innerHTML = event.data + "\n";
	sock.send(event.data)
});

function showValue(newValue) {
	document.getElementById("valuebox").value = newValue;
}

$(document).ready(function() {
	$('#slidetest').range({
		min: 0.0,
		max: 2,
		start: 1,
		step: 0.01,
		input: '#testinput'
	});
	$('#slidetest2').range({
		min: 0,
		max: 10,
		start: 5,
		input: '#testinput2'
	});
	$('#slidetest3').range({
		min: 0,
		max: 10,
		start: 5,
		input: '#testinput3'
	});
});


