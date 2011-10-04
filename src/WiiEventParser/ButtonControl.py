#class that handles button presses from a wiimote
import cwiid #uses constant values of cwiid library for buttons
import WiiEvent

class ButtonControl:
	"""Class that keeps track of state of all buttons on a wiimote
	tests cwiid button events to see what buttons are pressed and released"""
	#constants for button presses from cwiid libarary
	BUTTONS = [cwiid.BTN_PLUS,cwiid.BTN_UP,cwiid.BTN_DOWN,cwiid.BTN_RIGHT, \
		cwiid.BTN_LEFT,cwiid.BTN_HOME,cwiid.BTN_MINUS,cwiid.BTN_A, \
		cwiid.BTN_B,cwiid.BTN_1,cwiid.BTN_2]
	#names for button presses
	BUTTON_NAMES = ['ButtonPlus','ButtonUp','ButtonDown','ButtonRight','ButtonLeft','ButtonHome', \
		'ButtonMinus','ButtonA','ButtonB','Button1','Button2']
	
	def __init__(self):
		"""default constructor, sets buttons to none pressed"""
		self.INIT_VALUES = [False,False,False,False,False,False,False,False,False,False,False]
		self.currentButtons = [self.BUTTON_NAMES,self.INIT_VALUES]
	
	def testEvent(self,timestamp,ID,newPressed):
		"""Tests new button combination for what buttons are pressed
		timestamp is timestamp of event
		ID is wiimote ID
		newPressed is the new button combination passed in the evnets"""
		newButtons = self.getNewState(newPressed)
		for x in range(len(self.currentButtons[0])):#iterates through all buttons
			if newButtons[x] and not self.currentButtons[1][x]:#test for button press
				triggeredEvent = WiiEvent.WiiEvent(ID,self.currentButtons[0][x],1,timestamp)
				triggeredEvent.fireEvent()	
			elif self.currentButtons[1][x] and not newButtons[x]:#test for button release
				triggeredEvent = WiiEvent.WiiEvent(ID,self.currentButtons[0][x],-1,timestamp)
				triggeredEvent.fireEvent()
			self.currentButtons[1][x] = newButtons[x] 
		
	def getNewState(self, newPressed):
		"""expands cwiid combination binary string into a set of boolean values
		iterates from the button first in the binary string (therefore the largest integer value)
		down to last in the binary string, using modulus to remove the high value buttons as they're tested"""
		newButtons = [False, False,False,False,False,False,False,False,False,False,False]#reset newbuttons 
		for x in range(len(self.BUTTONS)):#iterate through cwiid button values
			if newPressed >= self.BUTTONS[x]:#checks if current button is pressed
				newButtons[x] = True
			else:
				newButtons[x] = False
			newPressed = newPressed % self.BUTTONS[x]#remove the button from the cwiid value
		return newButtons	
