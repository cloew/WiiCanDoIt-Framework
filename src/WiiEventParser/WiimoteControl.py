import cwiid
import RawData
import socket

class WiimoteControl:
	"""Class that keeps track of a single wiimote object, controls feedback of the
	object, keeps a unique ID for the wiimote as well as the callback function that
	cwiid will call."""
	def __init__(self,newWiimote,newID = 0):
		"""constructor. sets id and wiimote, gets the calibration info to adjust all
		future acceleration values, and turns on the LED of the wiimote to match the ID"""
		self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.wiimote = newWiimote
		self.ID = newID
		self.wiimote.led = self.ID + 1
		self.setupDataRead()
		self.cal,max = self.wiimote.get_acc_cal(cwiid.EXT_NONE)


	def __del__(self):
		"""destructor. closes wiimote connection"""
		self.wiimote.close()

	def setupDataRead(self):
		"""sets up the wiimote to report button presses and acceleration data, and
		sets up the wiimote callback function"""
		self.wiimote.enable(cwiid.FLAG_MESG_IFC)

		reportMode = 0
		reportMode ^= cwiid.RPT_BTN
		reportMode ^= cwiid.RPT_ACC
	
		self.wiimote.rpt_mode = reportMode

		self.wiimote.mesg_callback = self.testForEvents

	def testForEvents(self,mesg_list,timestamp):
		"""callback funciton of the wiimote. creates and sends the raw data associated
		with each event received by the wiimote"""
		for mesg in mesg_list:
			if mesg[0] == cwiid.MESG_ACC:#if acceleration data, send a rawAcc object
				x,y,z = self.cal[0] - mesg[1][cwiid.X], mesg[1][cwiid.Y] - self.cal[1],mesg[1][cwiid.Z] - self.cal[2]
				data = RawData.RawAcc(self.ID,timestamp,x,y,z)
				data.fireData(self.clientSocket)
			elif mesg[0] == cwiid.MESG_BTN:#if button data, send a rawButton object
				data = RawData.RawButton(self.ID,timestamp,mesg[1])
				data.fireData(self.clientSocket)
