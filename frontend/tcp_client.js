var net = require('net');
var tcp_client = new net.Socket();
const timeout_length = 2000;
var address;

module.exports = {
	connect: connectServer,
	setHandler: setDataHandler
}

function connectServer(target_host, target_port) {
	address = { host: target_host, port: target_port };
	tcp_client.connect(address);
	return tcp_client;
}

function reconnectServer() {
	console.log('Reconnecting..');
	tcp_client.connect(address);
}

function setDataHandler(handler) {
	tcp_client.on('data', handler);
}

tcp_client.on('connect', function () {
	console.log('Connected.');
});

tcp_client.on('error', function (err) {
	console.error(err.code, err.message, 'Error at backend TCP.');
});

tcp_client.on('close', function (err) {
	console.log('Connection closed.');
	setTimeout(reconnectServer, timeout_length);
});

tcp_client.on('end', function (err) {
	console.log('Connection ended.');
	setTimeout(reconnectServer, timeout_length);
});

