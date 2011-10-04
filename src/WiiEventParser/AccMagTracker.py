import sys,os
try:
    import ParserSettings
except:
    filepath = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.dirname(filepath))
    import ParserSettings

class AccMagTracker:
	"""Class that keeps track of accelerometer magnitude, returns flick magnitude when test bound functions called"""
	def __init__(self):
		"""Constructor, sets timestamp, upper and lower bounds to zero"""
		self.upper, self.lower = 0,0
		self.timestamp = 0

	def testLowerBound(self,time,accel):
		"""Tests lower acceleration bound, 
		accel value is the individual axis acceleration from the most recent raw datai
		time is the most recent timestamp"""
		if (time - self.timestamp) > ParserSettings.TIME_DELTA:#tests lockout threshold of a flick event
			if accel > self.lower:#tests to see if the flick maximum is met yet, relative to the previous magnitude
				self.timestamp 	= time#set appropriate values when flick triggered
				toReturn 		= self.lower
				self.lower	 	= 0#reset flick for next magnitude test
				return toReturn
			else:
				self.lower = accel#if no flick yet, update most recent flick to test
				return 0
		else:
			return 0

	def testUpperBound(self,time,accel):
		"""Tests upper acceleration bound,
		accel value is the individual acceleration from the most recent raw data
		time is most recent timestamp"""
		if (time - self.timestamp) > ParserSettings.TIME_DELTA:#tests lockout threshold of a flick event
			if accel < self.upper:#tests if flick maximum is found, relative to previous magnitude
				self.timestamp	= time#once peak found, set appropriate data and return a flick
				toReturn		= self.upper
				self.upper		= 0
				return toReturn
			else:
				self.upper = accel#if no flick yet, update most recent flick to test
				return 0
		else:
			return 0

