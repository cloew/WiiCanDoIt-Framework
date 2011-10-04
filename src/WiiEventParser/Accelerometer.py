#Accelerometer Class
#Keeps track of timestamps on a particular wiimote accelerometer,
#fires events when the parser passes a certain threshold
import cwiid
import AccMagTracker
import WiiEvent

import sys,os
try:
	import ParserSettings
except:
	filepath = os.path.dirname(os.path.abspath(__file__))
	sys.path.append(os.path.dirname(filepath))
	import ParserSettings

class Accelerometer:
	"""Class for evaluating accelerometer data, keeps a wiimotes AccMagTracker
	objects, calls appropriate magnitude trackers"""
	def __init__(self):
		"""Default constructor, makes AccMagTracker objects"""	
		self.xTracker	= AccMagTracker.AccMagTracker()
		self.yTracker 	= AccMagTracker.AccMagTracker()
		self.zTracker	= AccMagTracker.AccMagTracker()

	def testEvent(self,timeStamp,ID,x,y,z):
		"""Tests event. x, y, z are calibrated wiimote accelerometer values. timestamp
		is passsed from the raw data. ID is wiimote id in event of flick. Function tests
		threshold values for each axis, calls AccMagTracker to detect flick if over a threshold.
		Fires flick event with magnitude if AccMagTracker doesnt Return 0"""
		if x > ParserSettings.X_POS:#if block to test thresholds for x direction
			self.yTracker.timestamp = timeStamp#Y FALSE POSITIVE GUARD: activates timeout in y if a flick in x is occuring
			mag = self.xTracker.testUpperBound(timeStamp,x)
			if mag != 0:
				triggeredEvent = WiiEvent.WiiEvent(ID,'FlickX',mag,timeStamp)
				triggeredEvent.fireEvent()	
		elif x < ParserSettings.X_NEG:
			self.yTracker.timestamp = timeStamp#Y FALSE POSITIVE GUARD: see above
			mag = self.xTracker.testLowerBound(timeStamp,x)
			if mag != 0:
				triggeredEvent = WiiEvent.WiiEvent(ID,'FlickX',mag,timeStamp)
				triggeredEvent.fireEvent()
		
		if y > ParserSettings.Y_POS:#if block to test thresholds in y direction
			mag = self.yTracker.testUpperBound(timeStamp,y)
			if mag != 0:
				triggeredEvent = WiiEvent.WiiEvent(ID,'FlickY',mag,timeStamp)
				triggeredEvent.fireEvent()
		elif y < ParserSettings.Y_NEG:
			mag = self.yTracker.testLowerBound(timeStamp,y)
			if mag != 0:
				triggeredEvent = WiiEvent.WiiEvent(ID,'FlickY',mag,timeStamp)
				triggeredEvent.fireEvent()


		if z > ParserSettings.Z_POS:#if block to test thresholds in z direction
			self.yTracker.timestamp = timeStamp#Y FALSE POSITIVE GUARD: see above
			mag = self.zTracker.testUpperBound(timeStamp,z)
			if mag != 0:
				triggeredEvent = WiiEvent.WiiEvent(ID,'FlickZ',mag,timeStamp)
				triggeredEvent.fireEvent()
		elif z < ParserSettings.Z_NEG:
			self.yTracker.timestamp = timeStamp#Y FALSE POSITIVE GUARD: see above
			mag = self.zTracker.testLowerBound(timeStamp,z)
			if mag != 0:
				triggeredEvent = WiiEvent.WiiEvent(ID,'FlickZ',mag,timeStamp)
				triggeredEvent.fireEvent()
