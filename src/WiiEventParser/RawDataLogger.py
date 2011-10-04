import time
import os
import pickle

class RawDataLogger:
	"""class that handles all logging of the raw data"""
	# Filehandle
	logfile = None

	def __init__(self):
		"""opens up the log file for the class"""
		path = os.path.dirname(os.path.abspath(__file__)) + "/log/" + str(time.time()) + ".txt"
		self.logfile = open(path, "wb")
		print "Started Logging to", path

	def log(self, rawData):
		"""uses pickle module to dump the rawData into the file"""
		pickle.dump(rawData, self.logfile, pickle.HIGHEST_PROTOCOL)

	def close(self):
		"""closes the log file"""
		print "Closed the Wii Event Parser log file"
		self.logfile.close()

	def __del__(self):
		"""destructor"""
		self.logfile.close()
