import sys, os
import socket
import select
import copy
import time
from threading import Timer
import pickle

try:
	import WiiEvent
	import WEPControl
	import ParserSettings
	import WiiEventParser
except:
	filepath = os.path.dirname(os.path.abspath(__file__))
	sys.path.append(os.path.dirname(filepath))
	sys.path.append(os.path.dirname(filepath)+"/WiiEventParser")
	import WiiEvent
	import WEPControl
	import ParserSettings
	import WiiEventParser

import GameEventLogger
import WiiEventLogger

class GameEventCore:
	""" This is the Game Event Parser. This class is responsible
	for listening to the stream of Wii Events and transforming 
	them into game function calls."""

	##############################################
	# State lists
	# 	These lists store the current state of the
	#	bindings. See the documentation for an
	#	explanation of the data structure used.
	# List to store all the bindings defined in the
	# subclass
	bindings = [] 
	# List to store the pointers to the next event
	pointers = []
	# List to store the parameters to be sent 
	# to the callback function
	params = []
	# List to store the combos in progress
	combos = []
	# List to store the series in progress
	series = []
	# List to store any Flick combo
	flicks = []
	# List to store the timeout in progress
	timeout = []
	# List to store the binding that is holding the lock
	lock	= []
	##############################################

	# Pointer to the logger object
	wiilogger = None
	gamelogger = None
	# Boolean if logging is enabled
	_logging = True 

	_flickCombo = (ParserSettings.GEP_EVENT_FLICKX, 
					ParserSettings.GEP_EVENT_FLICKY, 
					ParserSettings.GEP_EVENT_FLICKZ)

	def __init__(self, players = None, other = None, logging = True):
		""" Initialize all the variables that will be used in the parser.
		If the *players* parameter is not specified, the parser will try
		to create a WEPControl object that uses a simple GUI to sync Wiimotes.
		The *other* parameter can be another GameEventCore object. The
		*logging* parameter indicates whether or not the parser should
		keep a log of received WiiEvents and game events"""
 
		self._numPlayers 	= players
		self._logging 		= logging	
		self._isRunning		= True
		self._serversocket  = None
		
		if self._logging:
			self.wiilogger = WiiEventLogger.WiiEventLogger()
			self.gamelogger = GameEventLogger.GameEventLogger()
		print "Started the Game Event Parser"

		'''# If they gave us another bindings object, use its WEPcontrol object
		if not other == None and isinstance(other, GameEventCore):
			self._WEPControl = 	other._WEPControl
		# otherwise, create a new WEPcontrol object
		else :
			self._WEPControl = WEPControl.WEPControl()'''
			

	# Destructor
	def __del__(self):
		""" Close the loggers if logging is enabled. """
		if self._logging:
			self.wiilogger.close()
			self.gamelogger.close()
	
	##############################################
	# Setup functions	
	##############################################
	def start(self):
		""" Set up the socket to listen for events from the Wii Event Parser
		then start listening on that socket"""
		self.initBindings()
		self._serversocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self._serversocket.bind( (ParserSettings.GEP_HOST, ParserSettings.GEP_PORT) )
		self._gameSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			
		self.listen()

	# listen for connections on the specified port
	def listen(self):
		""" Listen for Wii events from the WEP. If any input is received 
		from the standard in, stop listening. This is makes it easy to 
		stop the parser and therefore, free up the socket. """
		input = [self._serversocket, sys.stdin]
		running = 1
		while running:
			inputready, outputready, exceptready = select.select(input, [], [])			

			for s in inputready:
				if s == self._serversocket:
					receivedEvent, location = self._serversocket.recvfrom(1024)
					self.receiveWii(receivedEvent)
				elif s == sys.stdin:
					junk = sys.stdin.readline()
					running = 0

	def end(self):
		""" Close the sockets """
		self._serversocket.close()
		self._gameSocket.close()

	# Build the data structures necessary for storing information about
	# the state of the bindings	
	def initBindings(self):
		""" Build the data structures needed by the parser. """
		if self._numPlayers == None:
			print "You must specify the number of players. Exiting."
			sys.exit()	
	
		members = dir(self)
		# Set up the state lists for each player
		for player in range(self._numPlayers):
			self.bindings.append({})
			self.pointers.append({})
			self.params.append({})
			self.combos.append({})
			self.series.append({})
			self.timeout.append({})
			self.flicks.append({})
			self.lock.append(None)	

			# Some state lists store dictionaries with
			# the bindings as the keys
			for binding in members:
				if( binding[0:ParserSettings.GEP_BIND_PREFIX_LEN] ==
					ParserSettings.GEP_BIND_PREFIX):
					self.bindings[player][binding] 	= getattr(self, binding)
					self.replaceFlickCombos(player, binding)
					self.pointers[player][binding] 	= self.bindings[player][binding][0]
					self.params[player][binding]	= {
										'player':		0,
										'duration':		0,
										'flickx':		0, 
										'flicky':		0,
										'flickz':		0,
										'pitch':		0,
										'roll':			0}
					self.combos[player][binding]	= {
										'events':		[],
										'startTime':	None}
					self.series[player][binding]	= {
										'event':	None,
										'count':	0,
										'timer':	None}	
					self.timeout[player][binding]	= None
					self.flicks[player][binding]	= {
										'events':	[],
										'startTime': None,
										'timer': 	None}

	def replaceFlickCombos(self, player, binding) :
		""" Expand any generic 'Flick' in the bindings to be a combo
		of flicks in any direction. """
		x = 0
		for event in self.bindings[player][binding]:
			if event == ParserSettings.GEP_EVENT_FLICK:
				self.bindings[player][binding][x] = self._flickCombo
			x += 1			


	# Wrapper for WEP functions
	def addWiimotes(self, count = None):
		""" Warning. This function is not recommended for use. The
		game should be in charge of adding Wiimotes. This is only
		included because the parser won't work unless it knows the 
		number of wiimotes."""
		if not count == None:
			self._numPlayers = count
		self._WEPControl.WiimoteGui(self._numPlayers)
		self._numPlayers = self._WEPControl._numMotes	

	####################################################
	### Parser functions
	####################################################


	####################################################
	### Abandon hope all ye who enter here. 
	### Your journey will be fraught with peril. Beware
	### the endless thorny branches. Ravenous untested
	### code lurks in every path.
	####################################################
	def receiveWii(self, wiiEventString ):
		"""Decompress the pickle string, log it, and send the event to the parser."""
		# Convert the wiiEvent string into a wiiEvent object
		wiiEvent = WiiEvent.WiiEvent()
		wiiEvent.deCompressEvent( wiiEventString )
	
		#if not str(wiiEvent) in ParserSettings.GEP_FILTER_EVENTS:
		#	print "Received", str(wiiEvent), "for player", wiiEvent.wiimoteID, wiiEvent.time, wiiEvent.modifier

		if self._logging:
			self.wiilogger.log(wiiEvent)

		self.parseEvent(wiiEvent)


	def parseEvent(self, wiiEvent):
		""" This is the meat of the GameEventParser. All kinds of craziness begins here. There are too many branches
		to explain in a docstring, so if you want to understand how it works, you can try deciphering the code, 
		or email me at sdaugher@mines.edu. I'll help you. Really I will. """
		for player in range(self._numPlayers):
			for binding in self.bindings[player]:
				# First, only look at this event if it is for this player
				if wiiEvent.wiimoteID == player:
					# If there is a timeout set or a different binding has a lock,
					# ignore the received event
					if not self.hasTimeOut(player, binding) and not self.lockedOut(player, binding): 
						if not self.filterEvent(player, binding, wiiEvent):	
							# update the start time if this is the first event
							if( self.params[player][binding]['duration'] == 0 ) :
								self.params[player][binding]['duration'] = wiiEvent.time					
							# If there was a series running, close it up
							if( self.activeSeries(player, binding) and not str(wiiEvent) == self.series[player][binding]['event'] ):
								self.finishSeries(player, binding, wiiEvent)

							if self.isFlick(wiiEvent):
								self.parseFlick(player, binding, wiiEvent)
							# Combos are parsed differently than regular events			
							elif(self.activeCombo(player, binding)):
								self.parseCombo(player, binding, wiiEvent)
							elif str(wiiEvent) in ParserSettings.GEP_SERIES_EVENTS:
								self.parseSeries(player, binding, wiiEvent)
							else:
								self.parseSequence(player, binding, wiiEvent)
	
	def advancePointer(self, player, binding, endTime):
		""" After an event matches in the binding sequence, try to 
		move the pointer to the next event in the sequence. If the 
		pointer was at the end of the sequence, call the game function
		then reset the pointer. """
		pointer = self.pointers[player][binding]
		currentIndex = self.bindings[player][binding].index(pointer)
		# only advance if we didn't reach the end of the list
		if( currentIndex+1 < len(self.bindings[player][binding])):  
			self.pointers[player][binding] = self.bindings[player][binding][currentIndex+1]
		# if we were at the end of the list, call the callback
		# and reset the binding
		else:
			self.sendGameEvent(player, binding, endTime)	

	def resetBinding(self, player, binding):
		""" Reset the pointer, combos object, and the params object """
		self.pointers[player][binding] = self.bindings[player][binding][0]
		self.combos[player][binding] = {'events': [], 
										'startTime': None}
		self.params[player][binding]['duration'] = 0
		self.params[player][binding]['flickx'] = 0
		self.params[player][binding]['flicky'] = 0
		self.params[player][binding]['flickz'] = 0
		self.flicks[player][binding] = {'events': [], 
										'startTime': None, 
										'timer': None}


	def examineNextPointer(self, player, binding):
		""" If the next event is a special event like a timeout, do whatever
		that event specifies. """
		pointer = self.pointers[player][binding]
		currentIndex = self.bindings[player][binding].index(pointer)
		if currentIndex+1 < len(self.bindings[player][binding]) :
			nextPointer = self.bindings[player][binding][currentIndex+1]
			# If the next pointer is a timeout event, 
			# set a timeout for the specified seconds
			equalsPos = ParserSettings.GEP_EVENT_TIMEOUT.find('=')
			if( nextPointer[0:equalsPos] == ParserSettings.GEP_EVENT_TIMEOUT[0:equalsPos]) :
				#self.timeout[player][binding] = nextPointer[equalsPos+1:] 
				self.advancePointer(player, binding, time.time())
			elif nextPointer == ParserSettings.GEP_EVENT_LOCK:
				# This binding wants a lock, so lets set it
				self.lock[player] = binding
				# Let's also reset all other pointers for this player
				for bind in self.pointers[player]:	
					if not bind == binding:
						self.resetBinding(player, bind)
				self.advancePointer(player, binding, time.time())
			elif nextPointer == ParserSettings.GEP_EVENT_RELEASE_LOCK:
				# This binding is trying to give up its lock
				if self.lock[player] == binding:
					self.lock[player] = None
				# Don't forget to advance the pointer
				self.advancePointer(player, binding, time.time())


	def parseAtomicEvent(self, player, binding, wiiEvent) :
		""" Atomic events are the simplest to parse. This just needs to check 
		to see if the binding was expecting this event. """
		if( self.pointers[player][binding] == str(wiiEvent) ):
			# The event was the one we expected in the sequence, so 
			# look at the next pointer
			self.examineNextPointer(player, binding)
			
			# Now advance the pointer (Note that examineNextPointer might
			# have also advanced the pointer. That's ok. 
			self.advancePointer(player, binding, wiiEvent.time)
		else:
			self.resetBinding(player, binding)

	def parseSet(self, player, binding, wiiEvent):
		""" A set is a sequence of optional events. This allows the same
		function to be bound to multiple button presses. """
		pointer = self.pointers[player][binding]
		if str(wiiEvent) in pointer:
			# At least one of the items in the set was triggered
			# so we should advance the pointer
			self.examineNextPointer(player, binding)
			self.advancePointer(player, binding, wiiEvent.time)
		else:
			self.resetBinding(player, binding)

	def parseCombo(self, player, binding, wiiEvent):
		""" Combos are events that should happen at the same time.
		If there is a combo in progress, we need to treat the current event 
		differently than regular events."""

		# If the wiiEvent is in the current pointer and it happened quick enough, 
		# it is part of this combo.
		if str(wiiEvent) in self.pointers[player][binding] and abs(wiiEvent.time - self.combos[player][binding]['startTime']) < ParserSettings.GEP_COMBO_TIMEOUT :
			if not str(wiiEvent) in self.combos[player][binding]:
				# The combo is waiting for this event, so let's stick it in	
				self.combos[player][binding]['events'].append(wiiEvent)
			
				# Check if the combo is complete.
				if(self.comboComplete(player, binding)):
					# Update any flicks in the params
					for event in self.combos[player][binding]['events']:
						if str(event) == 'FlickX':
							self.params[player][binding]['flickx'] = event.modifier
						elif str(event) == 'FlickY':
							self.params[player][binding]['flicky'] = event.modifier
						elif str(event) == 'FlickZ':
							self.params[player][binding]['flickz'] = event.modifier

					self.examineNextPointer(player, binding)
					self.advancePointer(player, binding, wiiEvent.time)
					self.combos[player][binding]['startTime'] = None
					self.combos[player][binding]['events'] = []
			else: 
				# The wiiEvent was already in this combo! 	
				# This binding is no longer a match
				self.resetBinding(player, binding)
		else:
			# Not part of the combo (or it was too slow)
			# reset this binding to the first in the sequence
			self.resetBinding(player, binding)

	def startCombo(self, player, binding, wiiEvent) :
		self.combos[player][binding]['startTime'] = wiiEvent.time
		self.combos[player][binding]['events'].append(wiiEvent)

	
	def activeCombo(self, player, binding):
		""" Check if this binding has a combo in progress. """
		if self.combos[player][binding]['events'] == []:
			return False
		else:
			return True

	def comboComplete(self, player, binding) :
		""" Check if all the events the combo is expecting have happened. """
		if( len(self.combos[player][binding]['events']) == len(self.pointers[player][binding])):
			for event in self.combos[player][binding]['events']:
				if( not str(event) in self.pointers[player][binding] ):
					return False
			# If the loop didn't return false, 
			return True
		else:
			return False

	def parseSeries( self, player, binding, wiiEvent):
	
		pointer = self.pointers[player][binding]
		currentIndex = self.bindings[player][binding].index(pointer)
		# If this is the last event in the binding, 
		# set a timer to trigger the event
		if currentIndex+1 == len(self.bindings[player][binding]):
			self.series[player][binding]['timer'] = Timer(ParserSettings.GEP_ROLL_TIMEOUT, self.finishSeries, [player, binding, wiiEvent])
			self.series[player][binding]['timer'].start()
		 	
					
		# start the series if it isn't already	
		if not self.series[player][binding]['event']:
			self.series[player][binding]['event'] = str(wiiEvent)
			self.series[player][binding]['count'] += wiiEvent.modifier
		# if this event fits the series, increase the counter
		elif self.series[player][binding]['event'] == str(wiiEvent):
			self.series[player][binding]['count'] += wiiEvent.modifier
		# Otherwise this event doesn't fit the series, 
		# so we should move on
		else:
			print "Didn't match"
			

	def finishSeries(self, player, binding, wiiEvent):
		""" When the series is finished, update the params object, then reset the binding. """
		pointer = self.pointers[player][binding]
		currentIndex = self.bindings[player][binding].index(pointer)
		if len(self.bindings[player][binding]) > currentIndex+1:
			nextEvent = self.bindings[player][binding][currentIndex+1]
			# If the event we just received was supposed to come after the series,
			# update the parameters object
			if( str(wiiEvent) == nextEvent or str(wiiEvent) in nextEvent ):
				event = self.series[player][binding]
				self.params[player][binding][event['event'].lower()] = event['count']
	
			# now reset the series
			self.series[player][binding]['event'] = None
			self.series[player][binding]['count'] = 0
			self.series[player][binding]['timer'] = None

			# advance the pointer too
		self.advancePointer(player, binding, wiiEvent.time)

	def activeSeries(self, player, binding):
		""" Check if the current binding has a series in progress. """
		if( self.series[player][binding]['event'] ):
			return True
		else:
			return False

	def hasTimeOut(self, player, binding):
		""" Is there a timeout active for the current binding
		 If there is an expired timeout, reset the variable to None. """
		# First, is there something in the variable
		if self.timeout[player][binding]:
			# Now, is it expired?
			if time.time() < self.timeout[player][binding]:
				return True
			else:
				self.timeout[player][binding] = None
				return False 
		else:
			return False

	def lockedOut(self, player, binding):
		if not self.lock[player] or self.lock[player] == binding:
			return False			
		else:
			return True



	def inNextEvent(self, player, binding, wiiEvent):
		pointer = self.pointers[player][binding]
		currentIndex = self.bindings[player][binding].index(pointer)
		if( currentIndex + 1 < len(self.bindings[player][binding]) ):
			nextPointer = self.bindings[player][binding][currentIndex+1]
			if str(wiiEvent) == nextPointer or str(wiiEvent) in nextPointer:
				return True
			else:
				return False
		else:
			return False


	# 
	def filterEvent(self, player, binding, wiiEvent):
		""" The event will be discarded unless the current pointer
		 is looking for this event. """
		pointer = self.pointers[player][binding]
		# If this event isn't in the filtered list, there's no problem
		if str(wiiEvent) in ParserSettings.GEP_FILTER_EVENTS:
			# The sequence wants this event, so don't filter it
			if str(wiiEvent) == pointer:
				return False
			else:
				return True
		else:
			return False	

	# Parse a regular event. This method's name may be misleading
	def parseSequence(self, player, binding, wiiEvent):
		# Parse this event differently depending on if the pointer is 
		# pointing to a set, tuple or string
		pointer = self.pointers[player][binding]
		if( isinstance(pointer, str) ) :
			self.parseAtomicEvent(player, binding, wiiEvent)
		elif ( isinstance(pointer, tuple) ) :
			# We will only ever get here if this is the first event in
			# a combo
			self.startCombo(player, binding, wiiEvent)
		elif isinstance(pointer, set):
			self.parseSet(player, binding, wiiEvent)
		else:
			print "Unrecognized event"

	# See if this binding is looking for a 'Flick'
	def activeFlick(self, player, binding):
		if self.flicks[player][binding]['startTime'] == None:
				return False
		else:
			return True

	def parseFlick(self, player, binding, wiiEvent):
		eventName = str(wiiEvent)
		flick = ParserSettings.GEP_EVENT_FLICK
		
		# If the binding is looking for a flick, put this flick in the list
		pointer = self.pointers[player][binding]
		if pointer == str(wiiEvent) or str(wiiEvent) in pointer:
			# If this is the first flick, set the start time
			if self.flicks[player][binding]['startTime'] == None:
				self.flicks[player][binding]['startTime'] = wiiEvent.time
				try:
					self.flicks[player][binding]['timer'] = Timer(ParserSettings.GEP_COMBO_TIMEOUT, self.finishFlick, [player, binding, wiiEvent.time])				
					self.flicks[player][binding]['timer'].start()	
				except:
					print sys.exc_info()[0], sys.exc_info()[1]					
			self.flicks[player][binding]['events'].append( wiiEvent )


	# return the next event in the binding
	def getNextEvent(self, player, binding):
		nextPointer = None
		pointer = self.pointers[player][binding]
		currentIndex = self.bindings[player][binding].index(pointer)
		if( currentIndex+1 < len(self.bindings[player][binding]) ):
			nextPointer = self.bindings[player][binding][currentIndex+1]
	
		return nextPointer

	def updateFlickParams(self, player, binding, wiiEvent):
		eventName = str(wiiEvent)
		direction = eventName[len(eventName)-1:]
		if( direction.upper() == 'X' ):
			self.params[player][binding]['flickx'] = wiiEvent.modifier
		elif direction.upper() == 'Y' :
			self.params[player][binding]['flicky'] = wiiEvent.modifier
		elif direction.upper() == 'Z' :
			self.params[player][binding]['flickz'] = wiiEvent.modifier

	def isFlick(self, wiiEvent):
		eventName = str(wiiEvent)
		flick = ParserSettings.GEP_EVENT_FLICK
		if eventName[0:len(flick)] == flick:
			return True
		else:
			return False

	def flickExpired(self, player, binding, wiiEvent):
		if self.activeFlick(player, binding) :
			if abs(wiiEvent.time - self.flicks[player][binding]['startTime']) > ParserSettings.GEP_COMBO_TIMEOUT:
				return True
			else:
				return False
		else:
			return False

	def finishFlick(self, player, binding, endTime):
		# Update the parameters based on the contents of the flick
		for flickEvent in self.flicks[player][binding]['events']:
			self.updateFlickParams(player, binding, flickEvent)			

		self.flicks[player][binding]['events'] = []
		self.flicks[player][binding]['startTime'] = None
		self.flicks[player][binding]['timer'] = None
		# Advance the pointer
		self.advancePointer(player, binding, endTime)		
	
	def sendGameEvent(self, player, binding, endTime): 
		# First release any locks that this binding might have been holding
		if self.lock[player] == binding:
			self.lock[player] = None		

		self.params[player][binding]['player'] = player
		self.params[player][binding]['duration'] = float(endTime)- self.params[player][binding]['duration']
 
		funcParams = ( binding, self.params[player][binding] )
		if self._logging:
			self.gamelogger.log( funcParams )

		pickleFuncParams = pickle.dumps( funcParams, pickle.HIGHEST_PROTOCOL )	
		self._gameSocket.sendto(pickleFuncParams,(ParserSettings.GAME_HOST,ParserSettings.GAME_PORT)	)

		#if( callable(func) ):
		#	func(self.params[player][binding])
		self.resetBinding(player, binding)
	
	def removePointerEvent(self, pointer, wiiEvent):
		try:
			index = pointer.index(wiiEvent)
		except:
			return
		del pointer[index]

	def eventMatched(self, pointer, wiiEvent):
		# If pointer is a set, check that wiiEvent was in the set
		if( isinstance(pointer, set) ) :
			if( str(wiiEvent) in pointer ):
				return 1	# return true
			else:
				return 0	# return false
		# If pointer is a list, check that wiiEvent is in list
		elif( isinstance(pointer, list)) :
			try:
				index = pointer.index(wiiEvent)
				return 1	# return true
			except:
				return 0	# return false
		# If pointer is a string, check that wiiEvent matches the string
		elif( isinstance(pointer, str) and pointer == str(wiiEvent)):
			return 1		# return true
		else:
			return 0		# return false


