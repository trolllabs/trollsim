from misc import DataWriter
from processors import GloveMultiplier, Tunnel, AudioTrigger
from http.server import BaseHTTPRequestHandler


class ControlAPI(BaseHTTPRequestHandler):
	def __init__(self, modules):
		self.module_creator = modules
		self.logger = None
		self.running_modules = {}
		self.processors = {
				'gm': GloveMultiplier(),
				'at': AudioTrigger()
				}

	def __call__(self, *args):
		BaseHTTPRequestHandler.__init__(self, *args)

	def do_GET(self):
		path = self.path.split('/')[1:]
		if path[0] == 'status':
			self.get_status()
		elif path[0] == 'begin':
			if not self.logger:
				self.start_logging()
			else:
				self.send_response_header(409)
		elif path[0] == 'end':
			if self.logger:
				self.stop_logging()
			else:
				self.send_response_header(409)
		elif len(path) == 2:
			if path[0] == 'processor':
				self.run_processor_command(path[1])
			else:
				self.run_endpoint_command(path[0], path[1])
		else:
			self.send_response_header(404)

	def send_response_header(self, http_code):
		self.send_response(http_code)
		self.send_header('Content-type', 'text/html')
		self.end_headers()

	def write(self, data):
		self.wfile.write(data.encode())

	def run_endpoint_command(self, endpoint_name, command):
		if self.logger:
			if command == 'start':
				status_code = self.start_module(endpoint_name)
				self.send_response_header(status_code)
			elif command == 'stop':
				status_code = self.stop_module(endpoint_name)
				self.send_response_header(status_code)
			else:
				self.send_response_header(404)
		else:
			self.send_response_header(409)

	def run_processor_command(self, processor_name):
		if self.logger:
			if processor_name in self.processors:
				for module in self.processors[processor_name].endpoints:
					self.start_module(module)
				self.processors[processor_name].set_sources(self.running_modules)
				self.send_response_header(200)
		else:
			self.send_response_header(409)

	def get_status(self):
		status = 'Trollsim status\n================='
		if self.logger:
			status += '\nCurrently logging.'
			for endpoint in self.running_modules:
				status += '\n\t%s: running' % endpoint
		else:
			status += '\nIdle'
		status += '\n\n'
		self.write(status)
		self.send_response_header(200)

	def start_module(self, module_name):
		res = 200
		if module_name not in self.running_modules:
			if module_name in self.module_creator.modules:
				new_module = self.module_creator.create_module(module_name)
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

	def start_logging(self):
		if not self.logger:
			try:
				self.logger = DataWriter()
				self.write('Begin log session.\n')
				for module in self.running_modules:
					self.logger.add_endpoint(self.running_modules[module])
				return 200
			except IOError:
				logging.exception('Datalogger IO error.')
				return 409
		else:
			return 409

	def stop_logging(self):
		if self.logger:
			self.logger.dispose()
			for module in self.running_modules:
				self.running_modules[module].stop()
			self.running_modules = {}
			self.write('End log session.\n')
			self.logger = None
			return 200
		else:
			return 409

