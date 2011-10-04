import time
import os
import pickle

class WiiEventLogger:
	# Filehandle
	logfile = None	

	def __init__(self):
		path = os.path.dirname(os.path.abspath(__file__)) + "/wiiEventLog/" + str(time.time()) + ".txt"
		self.logfile = open(path, "wb")

	def log(self, wiiEvent):
		pickle.dump(wiiEvent, self.logfile, pickle.HIGHEST_PROTOCOL) 
	
	def close(self):
		self.logfile.close()
