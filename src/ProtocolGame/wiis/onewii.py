import Accelerometer
import ButtonControl
import RollPitch

import ParserSettings

# a parser for just one wii data
class oneWii :
	def __init__(self):
		self.accelerometer = Accelerometer.Accelerometer()
		self.buttons = ButtonControl.ButtonControl()
		self.rollPitch = RollPitch.RollPitch()

	def __call__(self,ts,wid,xyz=None,buttons=None):
		if xyz is not None :
			self.accelerometer.testEvent( ts, wid, *xyz )
			self.rollPitch.testEvent( ts, wid, *xyz )
		if buttons is not None :
			self.buttons.testEvent( ts, wid, buttons )

