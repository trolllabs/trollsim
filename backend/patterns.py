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


class PacketFactory:
	def __init__(self, metadata):
		self.lookup = metadata

	def from_binary(self, binary_packet):
		packet_id = binary_packet[0]
		return TrollPacket(self.lookup['ids'][str(packet_id)], binary_packet=binary_packet)

	def from_name(self, name, value):
		return TrollPacket(self.lookup['names'][name], value=value)

	def from_id(self, packet_id, value):
		return TrollPacket(self.lookup['ids'][str(packet_id)], value=value)


class ModuleFactory:
	def __init__(self, config, meta):
		self.config = config
		self.meta = meta
		self.modules = {}

	def new_module(self, name, classtype):
		self.modules[name] = lambda : classtype(self.config[name], self.meta)

	def create_module(self, name):
		new_module =  self.modules[name]()
		new_module.name = name
		return new_module

