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

http.listen(port, function() {
	console.log('Web server listening to port ' + port);
});



// Placeholder solution for python-websockets
const WebSocket = require('ws');
const wss = new WebSocket.Server({ server: http });

var tcp_client = require('./tcp_client')
var socket_client = tcp_client.connect('localhost', 8005);

wss.on('connection', function connection(ws) {
	console.log('Number of clients: ' + wss.clients.size);

	ws.on('message', function incoming(message) {
		socket_client.write(message);
	});

	ws.send('Connected');
});

wss.on('close', function close() {
	console.log('A client disconnected.');
});

function getSocketData(message) {
	wss.clients.forEach(function each(client) {
		if (client.readyState == WebSocket.OPEN) {
			client.send(message);
		}
	});

}

tcp_client.setHandler(getSocketData);

