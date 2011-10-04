import sys,os
import pickle
try:
    import ParserSettings
except:
    filepath = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.dirname(filepath))
    import ParserSettings

class RawData:
	"""class to hold a standardized version of the Cwiid raw data"""
	def compressData(self):
		"""serializes the data by python's pickle module"""
		compressed = pickle.dumps(self,pickle.HIGHEST_PROTOCOL)
		return compressed

	def deCompressData(self,compressed):
		"""deserializes the pickled data, compressed is the pickled string"""
		decompressed = pickle.loads(compressed)
		self = decompressed

	def fireData(self,clientSocket):
		"""compresses and sends the data contained in itself over clientSocket"""
		try:
			clientSocket.sendto(self.compressData(),('localhost',ParserSettings.WEP_PORT))
		except:
			print 'ERROR:', sys.exc_info()[0],sys.exc_info()[1]
			return

class RawAcc(RawData):
	"""instance of RawData that keeps track of acceleration values"""
	def __init__(self,newID,timestamp,x,y,z):
		"""constructor that takes wiimoteID, timestamp of the event, x, y, and z acceleration values"""
		self.x,self.y,self.z = x,y,z
		self.wiimoteID = newID
		self.timestamp = timestamp

class RawButton(RawData):
	"""instance of RawData that keeps track of button presses"""
	def __init__(self,newID,timestamp,buttons):
		"""construtor that takes wiimoteID, timestamp, and button action (PressA, ReleaseB, etc)"""
		self.wiimoteID = newID
		self.timestamp = timestamp
		self.buttons = buttons
		
