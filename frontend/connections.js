module.exports = {
	init: initConnections
}

const WebSocket = require('ws');
const tcp_client = require('./tcp_client')
var metadata;
var wss;
function initConnections(http) {
	wss = new WebSocket.Server({ server: http });
	wss.on('connection', wssConnectionHandler);
	wss.on('close', function close() {
		console.log('A client disconnected.');
	});


	tcp_client.setHandler(getSocketData);
	var socket_client = tcp_client.connect('localhost', 8005);
	socket_client.on('connect', function () {
		if (!metadata)
			socket_client.write('metadata');
	});
}

function wssConnectionHandler(ws) {
	console.log('Number of clients: ' + wss.clients.size);

	ws.on('message', function incoming(message) {
		message = message.split(' ');
		packet = createPacket(message[0], message[1]);
		socket_client.write(packet);
	});
}

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

function getSocketData(message) {
	if (!metadata) {
		metadata = JSON.parse(message);
		console.log('Received metadata from server.');
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


