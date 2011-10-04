import time
import os
import pickle

class GameEventLogger:
	# Filehandle
	logfile = None	

	def __init__(self):
		path = os.path.dirname(os.path.abspath(__file__)) + "/gameEventLog/" + str(time.time()) + ".txt"
		self.logfile = open(path, "wb")

	def log(self, funcParams):
		pickle.dump(funcParams, self.logfile, pickle.HIGHEST_PROTOCOL) 
	
	def close(self):
		self.logfile.close()
