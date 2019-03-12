var express = require('express');
var app = express();
var http = require('http').createServer(app);
var port = 8000;

app.use(express.static('public', {root: __dirname}));

app.get('/', function(req, res) {
	res.sendFile('main.html', {root: __dirname});
});

app.get('/test', function(req, res) {
	res.sendFile('test.html', {root: __dirname});
});

app.get('/smoothie', function(req, res) {
	res.sendFile('smoothie.html', {root: __dirname});
});

app.get('/smoothie2', function(req, res) {
	res.sendFile('smoothie2.html', {root: __dirname});
});

app.get('/dref', function(req, res) {
	res.sendFile('dref.html', {root: __dirname});
});



// Placeholder solution for python-websockets
const WebSocket = require('ws');
const wss = new WebSocket.Server({ server: http });

var tcp_client = require('./tcp_client')
var socket_client = tcp_client.connect('localhost', 8005);

function createPacket(packet_id, packet_value) {
	let id = parseInt(packet_id, 10) + 1;
	let id_buffer = Buffer.from([id]);
	let value_buffer = Buffer.allocUnsafe(4);

	if (metadata['ids'][id]['type'] == 'float')
		value_buffer.writeFloatBE(parseFloat(packet_value));
	else
		value_buffer.writeInt32BE(packet_value);

	return Buffer.concat([id_buffer, value_buffer]);
}

wss.on('connection', function connection(ws) {
	console.log('Number of clients: ' + wss.clients.size);

	ws.on('message', function incoming(message) {
		message = message.split(' ');
		packet = createPacket(message[0], message[1]);
		socket_client.write(packet);
	});
});

wss.on('close', function close() {
	console.log('A client disconnected.');
});


var metadata;
function getSocketData(message) {
	if (!metadata) {
		metadata = JSON.parse(message);
		//metadata = {"ids": {"name": "hello", "type": "float"}};
		console.log('Received metadata from server. Starting up web server.');

		http.listen(port, function() {
			console.log('Web server listening to port ' + port);
		});
	}
	else {
		let id = message[0];
		let value;
		if (metadata['ids'][id]['type'] === 'float')
			value = message.readFloatBE(1);
		else
			value = message.readInt32BE(1);
		wss.clients.forEach(function each(client) {
			if (client.readyState == WebSocket.OPEN) {
				client.send(id + ' ' + value);
			}
		});
	}
}

tcp_client.setHandler(getSocketData);

