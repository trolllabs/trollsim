"""
.. module:: patterns

Patterns is a collection of pattern implementation. Currently only
subscribe pattern and something resembling factory pattern.
"""

import threading, struct
from misc import type_lookup
from datastructures import TrollPacket


class Observable:
	"""
	Implementation of the observer pattern through callbacks.
	"""
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
	"""
	Should hold uninstantiated objects of modules in dictionary, but
	can also provide a lookup for existing processors.

	Can otherwise instantiate modules when asked through create_modules.
	"""
	def __init__(self, config):
		self.config = config
		self.modules = {}
		self.processors = {}

	def new_processor(self, name, classtype):
		self.processors[name] = classtype()

	def new_module(self, name, classtype):
		"""
		Adds a new module to available modules (self.modules) for later
		instatiation in self.create_modules.

		The module, when instatiated will have the config passed in as
		argument (lambda).

		The name argument has to exist in self.config (or config.json)

		:param name: Name of a module
		:param classtype: An endpoint (or referred to incosistently as
		"module")

		:type name: str
		:type classtype: ObservableComponent
		"""
		self.modules[name] = lambda : classtype(self.config[name])

	def create_module(self, name):
		"""
		Instantiates and returns a module. This module has to exist in
		self.modules, and the name has to exist in config.

		:param name: Name of a module to be instantiated.
		:type name: str

		:return: ObservableComponent
		"""
		new_module =  self.modules[name]()
		new_module.name = name
		return new_module

