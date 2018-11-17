import sys, serial, logging
from _thread import start_new_thread


class ArduinoReader:
	def __init__(self, serial_reader):
		self.reader = serial_reader
		self.listeners = []

	def add_listener(self, listener):
		self.listeners.append(listener)

	def _notify_listeners(self, message):
		for listener in self.listeners:
			listener(message)

	def _run(self):
		for data in self.reader():
			self._notify_listeners(data)

	def __call__(self):
		start_new_thread(self._run, ())


class SocketReader:
	def __init__(self, socket_reader):
		self.listeners = []
		self.reader = socket_reader

	def add_listener(self, listener):
		self.listeners.append(listener)

	def _notify_listeners(self, message):
		for listener in self.listeners:
			listener(message)

	def _run(self):
		for data in self.reader():
			self._notify_listeners(data)

	def __call__(self):
		start_new_thread(self._run, ())

