var express = require('express');
var app = express();
var http = require('http').createServer(app);
var port = 8000;

app.use(express.static('public', {root: __dirname}));

app.get('/', function(req, res) {
	res.sendFile('main.html', {root: __dirname});
});

http.listen(port, function() {
	console.log('Web server listening to port ' + port);
});



// Placeholder solution for python-websockets
const WebSocket = require('ws');
const wss = new WebSocket.Server({ server: http });

var net = require('net');
var socket_client = new net.Socket();
socket_client.connect(8005, 'localhost', function() {
	console.log('Backend connected.');
	socket_client.setEncoding('utf-8');
});

wss.on('connection', function connection(ws) {
	console.log('Number of clients: ' + wss.clients.size);
	socket_client.on('data', function(data) {
		//console.log(data);
		wss.clients.forEach(function each(client) {
			if (client.readyState == WebSocket.OPEN) {
				client.send(data);
			}
		});
	});

	ws.on('message', function incoming(message) {
		socket_client.write(message);
	});

	ws.send('Connected');
});

wss.on('close', function close() {
	console.log('A client disconnected.');
});

