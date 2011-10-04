import cwiid
import sys
import WiimotePairing

def testAcceleration():
	wiimote = WiimotePairing.PairWiimote()

	print 'Setting message callback function: ',
	wiimote.mesg_callback = accCallbackFunction
	print 'PASSED'

	print 'Setting wiimote to handle accelerometer data: ',
	wiimote.rpt_mode = cwiid.RPT_ACC
	print 'PASSED'

	print 'Wiimote is now reading accelerometer data. to exit, enter 0'

	exit = 0
	while not exit:
		c = sys.stdin.read(1)
		if c == '0':
			exit = 1

	print 'EXITING PROGRAM'
	wiimote.close()

def accCallbackFunction(mesg_list,time):
	for mesg in mesg_list:
		if mesg[1][cwiid.X] > 175:
			print 'TIME: ', time, 'Wiimote was flicked to the right!'
		elif mesg[1][cwiid.X] < 75:
			print 'TIME: ', time, 'Wiimote was flicked to the left!'
		elif mesg[1][cwiid.Y] > 175:
			print 'TIME: ', time,  'Wiimote was flicked forward!'
		elif mesg[1][cwiid.Y] < 75:
			print 'TIME: ', time, 'Wiimote was flicked backward!'
		elif mesg[1][cwiid.Z] > 175:
			print 'TIME: ', time, 'the wiimote was flicked up!'
		elif mesg[1][cwiid.Z] < 75:
			print 'TIME: ', time, 'the wiimote was flicked down!'

testAcceleration()
