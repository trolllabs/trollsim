var express = require('express');
var app = express();
var http = require('http').createServer(app);
var port = 8000;
var connections = require('./connections.js');

app.use(express.static('public', {root: __dirname}));
connections.init(http);

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

http.listen(port, function() {
	console.log('Web server listening to port ' + port);
});

