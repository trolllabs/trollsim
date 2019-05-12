import logging
from misc import DataWriter
from processors import Tunnel
from datastructures import TrollPacket
from http.server import BaseHTTPRequestHandler


class AbstractedHTTPHandler(BaseHTTPRequestHandler):
	def __call__(self, *args):
		BaseHTTPRequestHandler.__init__(self, *args)

	def send_response_header(self, http_code):
		self.send_response(http_code)
		self.send_header('Content-type', 'text/html')
		self.end_headers()

	def write(self, data):
		self.wfile.write(data.encode())


class ControlAPI(AbstractedHTTPHandler):
	def __init__(self, modules):
		self.module_creator = modules
		self.logger = None
		self.running_modules = {}
		self.running_processors = {}
		self.processors = modules.processors

	def do_GET(self):
		path = self.path.split('/')[1:]
		if path[0] == 'status':
			self.get_status()
		elif (path[0] == 'tunnel') and (len(path) == 3):
			for module in path[1:]:
				if module not in self.running_modules:
					self.start_module(module)
			Tunnel(self.running_modules[path[1]], self.running_modules[path[2]])
			self.send_response_header(200)
		elif len(path) > 1:
			if path[0] == 'start':
				if path[1] == 'all':
					self.start_all()
				else:
					for path_segment in set(path[1:]):
						if path_segment == 'log':
							self.send_response_header(self.start_logging())
						elif path_segment in self.module_creator.modules:
							self.send_response_header(self.start_module(path_segment))
						elif path_segment in self.processors:
							self.send_response_header(self.start_processor(path_segment))
			elif path[0] == 'stop':
				if path[1] == 'all':
					self.stop_all()
				else:
					for path_segment in set(path[1:]):
						if path_segment == 'log':
							self.send_response_header(self.stop_logging())
						elif path_segment in self.running_modules:
							self.send_response_header(self.stop_module(path_segment))
						elif path_segment in self.running_processors:
							self.send_response_header(self.stop_processor(path_segment))
						else:
							self.send_response_header(409)
		else:
			self.send_response_header(404)

	def get_status(self):
		status = 'Trollsim status\n================='
		if self.logger:
			status += '\nCurrently logging.'
		else:
			status += '\nNot logging'
		status += '\n\nModules:'
		for endpoint in self.running_modules:
			status += '\n\t%s: running' % endpoint
		status += '\n\nProcessors:'
		for processor in self.running_processors:
			status += '\n\t%s: running' % processor
		status += '\n\n'
		self.write(status)
		self.send_response_header(200)

	def start_module(self, module_name):
		res = 200
		if module_name not in self.running_modules:
			if module_name in self.module_creator.modules:
				new_module = self.module_creator.create_module(module_name)
				if self.logger:
					self.logger.add_endpoint(new_module)
				new_module.start()
				self.running_modules[module_name] = new_module
			else:
				res = 404
		else:
			res = 409
		return res

	def stop_module(self, module_name):
		res = 200
		print('Stopping %s' % module_name)
		if self.running_modules.get(module_name, False):
			self.running_modules[module_name].stop()
			del self.running_modules[module_name]
			print('stopped')
		else:
			print('error')
			res = 404
		return res

	def start_processor(self, processor_name):
		if processor_name not in self.running_processors:
			if processor_name in self.processors:
				for module in self.processors[processor_name].endpoints:
					self.start_module(module)
				self.processors[processor_name].set_sources(self.running_modules)
				self.running_processors[processor_name] = self.processors[processor_name]
				return 200
		return 409

	def stop_processor(self, processor_name):
		if processor_name in self.running_processors:
			self.running_processors[processor_name].end_session()
			del self.running_processors[processor_name]
			return 200
		return 409

	def start_logging(self):
		if not self.logger:
			try:
				self.logger = DataWriter(self.module_creator.config, TrollPacket.meta)
				self.write('Begin log session.\n')
				for module in self.running_modules:
					self.logger.add_endpoint(self.running_modules[module])
				print('Started new log session')
				return 200
			except IOError:
				logging.exception('Datalogger IO error.')
				return 409
		else:
			return 409

	def stop_logging(self):
		if self.logger:
			self.logger.end_session()
			for module in self.running_modules:
				self.running_modules[module].stop()
			self.running_modules = {}
			self.write('End log session.\n')
			self.logger = None
			print('End log session')
			return 200
		else:
			return 409

	def start_all(self):
		result_summary = 'Start all (logging, modules, processors)\n'
		result_summary += 'Logging: %s\n' % self.start_logging()
		for module in self.module_creator.modules:
			result_summary += 'Module %s: %s\n' % (module, self.start_module(module))
		for processor in self.processors:
			result_summary += 'Processor %s: %s\n' % (processor, self.start_processor(processor))
		self.write(result_summary)
		self.send_response_header(200)

	def stop_all(self):
		result_summary = 'Stop all (logging, modules, processors)\n'
		result_summary += 'Logging: %s\n' % self.stop_logging()
		for processor in self.running_processors:
			self.running_processors[processor].end_session()
			result_summary += 'Processor %s: ok\n' % processor
		self.running_processors = {}
		for module in self.running_modules:
			self.running_modules[module].stop()
			result_summary += 'Endpoint %s: ok\n' % module
		self.running_modules = {}
		self.write(result_summary)
		self.send_response_header(200)

