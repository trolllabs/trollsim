import threading, struct
from misc import type_lookup
from datastructures import TrollPacket


class Observable:
	'''
	Implementation of the observer pattern through callbacks. External
	functions can read children classes through a callback handler with
	add_listener(callback)
	'''
	def __init__(self):
		self.listeners = []
		self.lock = threading.Lock()

	def add_listener(self, listener):
		self.listeners.append(listener)

	def _notify_listeners(self, message):
		for listener in self.listeners:
			listener(message)

	def remove_listener(self, listener):
		if listener in self.listeners:
			self.listeners.remove(listener)


class ModuleFactory:
	def __init__(self, config):
		self.config = config
		self.modules = {}
		self.processors = {}

	def new_processor(self, name, classtype):
		self.processors[name] = classtype()

	def new_module(self, name, classtype):
		self.modules[name] = lambda : classtype(self.config[name])

	def create_module(self, name):
		new_module =  self.modules[name]()
		new_module.name = name
		return new_module

