import sys
import cwiid

from onewii import oneWii

class WiimoteControl:
	def __init__(self, newWiimote, wid, wnum ):
		self.wiimote = newWiimote
		self.wiimote.led = wnum
		self.wid = wid
		self.setupDataRead()
		self.cal = max( self.wiimote.get_acc_cal(cwiid.EXT_NONE) )

		self.eventdetector = oneWii()

	def __del__(self):
		self.wiimote.close()

	def setupDataRead(self):
		self.wiimote.enable(cwiid.FLAG_MESG_IFC)

		reportMode = 0
		reportMode ^= cwiid.RPT_BTN
		reportMode ^= cwiid.RPT_ACC
	
		self.wiimote.rpt_mode = reportMode

		self.wiimote.mesg_callback = self.testForEvents

	def testForEvents(self,mesg_list,timestamp):
		for mesg in mesg_list:
			if mesg[0] == cwiid.MESG_ACC:
				# this appears backward but it isn't...
				x = self.cal[0] - mesg[1][cwiid.X] 
				y = mesg[1][cwiid.Y] - self.cal[1] 
				z = mesg[1][cwiid.Z] - self.cal[2]
				self.eventdetector(timestamp,self.wid,xyz=(x,y,z))
			elif mesg[0] == cwiid.MESG_BTN:
				self.eventdetector(timestamp,self.wid,buttons=mesg[1])


