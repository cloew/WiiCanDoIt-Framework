import cwiid
from threading import Thread
import socket
import select
import RawData
import pickle
import Accelerometer
import ButtonControl
import RollPitch
import RawDataLogger
import sys,os
try:
	import ParserSettings
except:
	filepath = os.path.dirname(os.path.abspath(__file__))
	sys.path.append(os.path.dirname(filepath))
	import ParserSettings

class WiiEventParser:
	"""class responsible for delegating analysis of raw data.
	reads raw data from a socket, and sends it to the appropriate analysis
	objects."""
	def __init__(self):
		"""construstor, sets up lists of analysis objects"""
		self._isRunning = True
		if ParserSettings.IS_LOGGING:
			self.logger = RawDataLogger.RawDataLogger()
		self.accelerometer = {}
		self.buttons = {}
		self.rollPitch = {}
		for x in range(7):
			self.accelerometer[x] = Accelerometer.Accelerometer()
			self.buttons[x] = ButtonControl.ButtonControl()
			self.rollPitch[x] = RollPitch.RollPitch()

	def __del__(self):
		"""destructor, closes logger"""
		if ParserSettings.IS_LOGGING:
			self.logger.close()

	def end(self):
		"""sets boolean value of running to false"""
		self._isRunning = False

	def start(self):
		"""Starts the socket read, calls the listen function"""
		print "Started the WEP"
		self._serversocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self._serversocket.bind( ('',ParserSettings.WEP_PORT) )
		
		self.listen()

	def listen(self):
		"""constantly listens from socket, calls events when data is found"""
		input = [self._serversocket, sys.stdin]
		running = 1
		while running:#loop for reading input
			inputready, outputready, exceptready = select.select(input, [], [])
			for s in inputready:
				if s == self._serversocket:
					theInput, location = self._serversocket.recvfrom(1024) 
					self.testForEvents(theInput)
				elif s == sys.stdin:
					junk = sys.stdin.readline()
					running = 0


	def testForEvents(self,rawString):
		"""loads pickled object, passes it to appropriate tests depending on ID and type of data"""
		rawData = pickle.loads(rawString)
		if ParserSettings.IS_LOGGING:
			self.logger.log(rawData)
		if hasattr(rawData,'x'):#if an object contains acceleration data, it will call the rollpitch and accelerometer tests 
			self.accelerometer[rawData.wiimoteID].testEvent(rawData.timestamp,rawData.wiimoteID,rawData.x,rawData.y,rawData.z)
			self.rollPitch[rawData.wiimoteID].testEvent(rawData.timestamp,rawData.wiimoteID,rawData.x,rawData.y,rawData.z)
		elif hasattr(rawData,'buttons'):#if an object contains button data, it will call buttonControl tests 
			self.buttons[rawData.wiimoteID].testEvent(rawData.timestamp,rawData.wiimoteID,rawData.buttons)
		else:#shouldnt be called, but this will prevent from an error breaking the parser 
			#if the data is corrupt or an unreckognized class
			print 'Could not find instance of rawData', rawData.__class__

