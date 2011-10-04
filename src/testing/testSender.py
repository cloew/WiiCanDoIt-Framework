import sys, os

try:
	import WiiEvent
except:
	filepath = os.path.dirname(os.path.abspath(__file__))
	sys.path.append(os.path.dirname(filepath))
	sys.path.append(os.path.dirname(filepath)+"/WiiEventParser")
	import WiiEvent

from testGame import *
import socket
import time
import pickle
from threading import Thread

class SimpleSender(Thread):
	def __init__(self):
		Thread.__init__(self)
		self.f = open('testEventList.txt', 'r')
		self._isRunning = True

	# Read WiiEvents from the log and send to the socket
	def run(self):
		while self._isRunning:
			try:
				loadedWiiEvent = pickle.load(self.f)
			except:
				print "Breaking"
				break
			clientsocket = socket.socket( socket.AF_INET, socket.SOCK_DGRAM)
			clientsocket.sendto( loadedWiiEvent.compressEvent(), ('localhost', 76543) )
			print "Sent: " + loadedWiiEvent.compressEvent()
			clientsocket.close()

	def end(self):
		self._isRunning = False

### End of class ####

sender = SimpleSender()

sender.start()

# Keep listening until we get a 'q'
running = True
while running:
	try:
		input = raw_input()
		input = input.strip()
		if( input == 'q' ):
			running = False
			sender.end()
	except KeyboardInterrupt:
		running = False
		sender.end()
