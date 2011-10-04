import sys,os

try:
	import RawData
	import WEPControl
except:
	filepath = os.path.dirname(os.path.abspath(__file__))
	sys.path.append(os.path.dirname(filepath)+'/WiiEventParser')
	import RawData
	import WEPControl

import socket
import time
import pickle
from threading import Thread

class testWEPSocket(Thread):
	def __init__(self):
		Thread.__init__(self)
		self.f = open('WEPTestLog.txt','r')
		self._isRunning = True

	def run(self):
		while self._isRunning:
			try:
				loadedEvent = pickle.load(self.f)
			except:
				print 'Breaking'
				break
			clientsocket = socket.socket( socket.AF_INET, socket.SOCK_STREAM)
			clientsocket.connect ( ('localhost',75154) )
			clientsocket.send( loadedEvent.compressData() )
			print "Sent: " + loadedEvent.compressData()
			clientsocket.close()

	def end(self):
		self._isRunning = False

parser = WEPControl.WEPControl()
testsocket = testWEPSocket()
testsocket.start()

running = True
while running:
	try:
		input = raw_input()
		input = input.strip()
		if( input == 'q' ):
			testsocket.end()
			running = False
	except KeyboardInterrupt:
		testsocket.end()
		running = False
	
