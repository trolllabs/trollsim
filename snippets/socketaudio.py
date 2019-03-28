'''
WRITTEN FOR WINDOWS

Play wav file based on socket signal
'''

import socket
from winsound import SND_LOOP as LOOP
from winsound import PlaySound, SND_FILENAME, SND_ASYNC


def playAudio(audio_path, loop=0):
	PlaySound(audio_path, SND_FILENAME | SND_ASYNC | loop)

def stopAudio():
	playAudio(None)


def main():
	port = 5050
	track1 = 'creative.wav'
	track2 = 'summer.wav'
	track3 = 'skype.wav'

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind(('0.0.0.0', port))
	sock.listen()
	print('TCP listening to %s' % port)

	conn, addr = sock.accept()
	print('%s:%s connected' % addr)

	while True:
		data = conn.recv(1024)
		if not data: break

		data = data.decode('utf-8').strip()
		if data == '1':
			print('Playing %s' % track1)
			playAudio(track1)
		elif data == '2':
			print('Playing %s' % track2)
			playAudio(track2)
		elif data == '3':
			print('Looping %s' % track3)
			playAudio(track3, LOOP)
		else:
			print('Stopping audio')
			stopAudio()

	print('Exiting')

if __name__ == '__main__':
	main()
