import sys,os

try:
	import WiimoteControl
except:
	filepath = os.path.dirname(os.path.abspath(__file__))
	sys.path.append(os.path.dirname(filepath) + '/WiiEventParser')
	import WiimoteControl

import cwiid

dummyVar = raw_input('Place the Wiimote in Discoverable mode and press ENTER:')

wiimote = cwiid.Wiimote()
id = 1

wiimoteControl = WiimoteControl.WiimoteControl(wiimote)

print 'To exit program, enter 0'
exit = 0
while not exit:
	c = sys.stdin.read(1)
	if c == '0':
		exit = 1
