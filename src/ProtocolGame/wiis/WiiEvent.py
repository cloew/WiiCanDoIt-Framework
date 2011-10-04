import sys,os

import ParserSettings

class WiiEvent:
	OUTBOUND = sys.stdout
	EVENT_FILTER = {}
	def __init__(self, wid, theName='0', theModifier=0, theTime=0):

		self.wiimoteID	= wid
		self.action     = theName
		self.modifier	= theModifier
		self.time  		= theTime

	def fireEvent(self):

		action = self.action + self.modifierToText()
		if self.EVENT_FILTER and ( action not in self.EVENT_FILTER ) :
			return
		dd = {}
		dd['action'] = action
		for k in ('wiimoteID','modifier','time') :
			dd[k] = getattr(self,k)

		self.OUTBOUND.write( str(dd)+"\n" )
		self.OUTBOUND.flush()

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

