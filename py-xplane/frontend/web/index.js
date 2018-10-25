var express = require('express')();
var http = require('http').createServer(express);
var port = 8000;


express.get('/', function(req, res) {
	res.sendFile('main.html', {root: __dirname});
});

http.listen(port, function() {
	console.log('Listening to port ' + port);
});

