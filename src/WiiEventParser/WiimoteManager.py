import sys,os
try:
	import ParserSettings
except:
	filepath = os.path.dirname(os.path.abspath(__file__))
	sys.path.append(os.path.dirname(filepath))
	import ParserSettings
import WiimoteControl

class WiimoteManager:
	def __init__(self):
		"""constructor. sets all wiimote objects to none objects"""
		self.wiimotes = [None,None,None,None,None,None,None]

		self.currentWiimote = 0
	def __del__(self):
		"""destructor. currently does nothing but notify it is being shut down"""
		print 'Destroying Wiimote Manager'

	def addWiimote(self, newWiimote):
		"""adds wiimote passed in to the list"""
		if self.currentWiimote >= ParserSettings.MAX_WIIMOTES:#tests if there is room for another wiimote
			print 'ERROR TOO MANY WIIMOTES CONNECTED'
		else:
			self.wiimotes[self.currentWiimote] = WiimoteControl.WiimoteControl(newWiimote,self.currentWiimote)
			self.currentWiimote = self.currentWiimote + 1
