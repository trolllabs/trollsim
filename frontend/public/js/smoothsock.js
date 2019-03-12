var flex = new TimeSeries();
var roll = new TimeSeries();
var pitch = new TimeSeries();
var yaw = new TimeSeries();

sock.addEventListener('message', function (e) {
	packet = e.data.split(' '); // First element is ID
	if (packet[0] == 1)
		flex.append(new Date().getTime(), packet[1]);
	else if (packet[0] == 2)
		roll.append(new Date().getTime(), packet[1]);
	else if (packet[0] == 3)
		pitch.append(new Date().getTime(), packet[1]);
	else if (packet[0] == 4)
		yaw.append(new Date().getTime(), packet[1]);
});

window.onload = function () {
	var chart = new SmoothieChart({
		grid: {fillStyle: '#F5F6F7', strokeStyle: 'transparent'},
		labels: {fillStyle: '#2C5573'},
		//scaleSmoothing: 1,
		minValue: -1.5,
		maxValue: 1.5,
		tooltip: true,
		responsive: true
	});
	chart.addTimeSeries(flex, {lineWidth: 2, strokeStyle: '#FA360A'});
	chart.addTimeSeries(roll, {lineWidth: 2, strokeStyle: '#EFDDB2'});
	chart.addTimeSeries(pitch, {lineWidth: 2, strokeStyle: '#1D556F'});
	chart.addTimeSeries(yaw, {lineWidth: 2, strokeStyle: '#288FB4'});
	chart.streamTo(document.getElementById('chart0'), 500);
}
