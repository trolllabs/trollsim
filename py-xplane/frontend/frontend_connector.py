import asyncio, websockets, random


async def recvmsg(websocket, path):
	print('ok')
	try:
		async for message in websocket:
			print(message)
		print('lost connection')
	except Exception as e:
		print('Error in receivemsg: %s' % str(e))


async def sendmsg(websocket, path):
	while True:
		await asyncio.sleep(1)
		await websocket.send(str(random.random()))


async def handler(websocket, path):
	msg_in = asyncio.ensure_future(recvmsg(websocket, path))
	msg_out = asyncio.ensure_future(sendmsg(websocket, path))
	done, pending = await asyncio.wait([msg_in, msg_out], return_when=asyncio.FIRST_COMPLETED)
	for task in pending:
		task.cancel()


start_server = websockets.serve(handler, '0.0.0.0', 8001)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

