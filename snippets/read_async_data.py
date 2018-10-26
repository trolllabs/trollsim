import random, asyncio
from time import sleep
from threading import Thread

'''
This snippet is to demonstrate using handlers to pull data out
from an async environment
'''

class AsyncDataGenerator:
	'''
	Async wrapper. We want this async thing contained. Securely contained.
	This is to avoid async creep.
	'''
	def __init__(self, handler):
		self.handler = handler
		self.loop = asyncio.new_event_loop()
		self.thread = Thread(target=self._start_loop, args=(self.loop,))
		self.thread.start()

	def _start_loop(self, loop):
		asyncio.set_event_loop(loop)
		loop.run_forever()

	async def _generate_values(self):
		'''
		Our asynchronous data source
		'''
		while True:
			await asyncio.sleep(0.2)
			self.handler(random.random())

	def run(self):
		return asyncio.run_coroutine_threadsafe(self._generate_values(), self.loop)


class ReadFromAsync:
	'''
	Handler class/wrapper
	'''
	def __init__(self):
		self.testvar = 0
	
	def async_handler(self, new_value):
		self.testvar = new_value
	
	def print_value(self):
		'''
		In the same thread, global sleeps are not allowed.
		Now that async is contained in its own separate thread, it will not
		be affected by a global sleep, hence the sleep below.
		'''
		while True:
			sleep(0.2)
			print(self.testvar)


reader = ReadFromAsync()
generator = AsyncDataGenerator(reader.async_handler)
generator.run()
reader.print_value()
