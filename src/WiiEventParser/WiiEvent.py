import socket
import pickle

import sys,os
try:
	import ParserSettings
except:
	filepath = os.path.dirname(os.path.abspath(__file__))
	sys.path.append(os.path.dirname(filepath))

class WiiEvent:
	SEPARATOR = '_'

	def __init__(self,wiiID=0,theName='0',theModifier=0,theTime=0):
		self.wiimoteID 		= int(wiiID)
		self.action 		= theName
		self.modifier 		= theModifier
		self.time	  		= theTime

	def compressEvent(self):
		compressed = pickle.dumps(self,pickle.HIGHEST_PROTOCOL)
		return compressed

	def deCompressEvent(self, event):
		exploded = pickle.loads(event)

		self.wiimoteID 	= exploded.wiimoteID
		self.action 	= exploded.action
		self.modifier 	= exploded.modifier
		self.time		= exploded.time

	def fireEvent(self):
		try:	
			clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			clientSocket.sendto(self.compressEvent(),('localhost',ParserSettings.GEP_PORT))
		except:
			print 'ERROR:', sys.exc_info()[0],sys.exc_info()[1]
			return

	"""
	Overload the equality operator
	"""
	def __eq__(self, other):
		return (self.wiimoteID == other.wiimoteID and self.action == other.action)

	def __str__(self):
		return self.action + self.modifierToText()

	def modifierToText(self) :
		# If this is a button press, make positive modifiers 
		# output 'Press' and negative modifiers 'Release'
		if( self.action[0:6] == "Button" ) :
			if( self.modifier > 0 ):
				return "Press"
			else :
				return "Release"
		# If this is a flick event, don't print the modifier
		elif( self.action[0:5] == 'Flick' or self.action[0:5] == 'Pitch' or self.action[0:4] == 'Roll' ) :
			return ''
		else :
			return string(self.modifier)
			 
