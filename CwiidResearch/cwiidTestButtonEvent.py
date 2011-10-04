import cwiid
import sys
import WiimotePairing

def testButtonEvent():
	wiimote = WiimotePairing.PairWiimote()
	
	print 'Setting message Callback Function:',
	wiimote.mesg_callback = buttonCallbackFunction
	print 'PASSED'
	
	print 'setting Wiimote to report button presses:',
	wiimote.rpt_mode = cwiid.RPT_BTN
	#	if wiimote.rpt_mode == cwiid.RPT_BTN:
	print 'PASSED'

	print 'Wiimote is now set up to handle button reporting. To exit press 0'
	exit = 0
	while not exit:
		c = sys.stdin.read(1)
		if c == '0':
			exit = 1

	print 'EXITING PROGRAM'
	wiimote.close()

def buttonCallbackFunction(mesg_list,time):
	print 'time:', time
	for mesg in mesg_list:
		message = hex(mesg[1])
		print 'Hex decimal of button presses:', message
		print 'Base ten version of button presses:', mesg[1]

testButtonEvent()	
