import math
import WiiEvent
import sys,os
try:
    import ParserSettings
except:
    filepath = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.dirname(filepath))
    import ParserSettings

class RollPitch:
	"""class that evaluates acceleration data to find the roll and pitch of the Wiimote,
	then compares it relative to the most recent threshold range the wiimote is remembered
	to be in""" 
	def __init__(self): 
		"""construstor sets the wiimote to be level"""
		self.currentRoll,self.currentPitch = 0.0,0.0

	def testEvent(self,timestamp,ID,x,y,z):
		"""tests to see if the current wiimote position needs to trigger an event.
		creates and sends the wii event if needed"""	
		x = -1 * x#flips x acceleration
		if z == 0:#since tangent will be x/z, z = 0 needs to be slightly adjusted to avoid DIVIDE BY 0
			z = .0000000001
		if abs(z) < ParserSettings.ROLL_PITCH_LOCKOUT_THRESHOLD and abs(x) < ParserSettings.ROLL_PITCH_LOCKOUT_THRESHOLD:
			#checks if there may be a roll or pitch occuring, where the accelerometers are spiking.
			#function doesnt test for a roll or pitch event if there is a flick occuring.
			#intent is to prevent false positives with roll and pitch events as much as possible.
			roll = math.atan(float(x)/float(z))#roll is calculated comparing calibrated x and z acceleration values
			pitch = math.atan(float(y)/float(z))*math.cos(roll)#pich is compared with calibrated y and z, modified by the roll
		
			if (roll - self.currentRoll) > ParserSettings.ROLL_THRESHOLD:
				#tests to see if the roll has changed enough to trigger an event
				triggeredEvent = WiiEvent.WiiEvent(ID,'Roll',1,timestamp)
				triggeredEvent.fireEvent()
				self.currentRoll = self.currentRoll + ParserSettings.ROLL_THRESHOLD
			elif(self.currentRoll - roll) > ParserSettings.ROLL_THRESHOLD:
				#tests for roll in other direction
				triggeredEvent = WiiEvent.WiiEvent(ID,'Roll',-1,timestamp)
				triggeredEvent.fireEvent()
				self.currentRoll = self.currentRoll - ParserSettings.ROLL_THRESHOLD
	
			if (pitch - self.currentPitch) > ParserSettings.PITCH_THRESHOLD:
				#tests pitch in same manner as role, relative to standard threshold
				triggeredEvent = WiiEvent.WiiEvent(ID,'Pitch',1,timestamp)
				triggeredEvent.fireEvent()
				self.currentPitch = self.currentPitch + ParserSettings.PITCH_THRESHOLD
			elif(self.currentPitch - pitch) > ParserSettings.PITCH_THRESHOLD:
				#tests other direction of pitch
				triggeredEvent = WiiEvent.WiiEvent(ID,'Pitch',-1,timestamp)
				triggeredEvent.fireEvent()
				self.currentPitch = self.currentPitch - ParserSettings.PITCH_THRESHOLD
