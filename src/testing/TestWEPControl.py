import sys,os
try:
	import WEPControl
except:
	filepath = os.path.dirname(os.path.abspath(__file__))
	sys.path.append(os.path.dirname(filepath) + '/WiiEventParser')
	import WEPControl

control = WEPControl.WEPControl()
#nummotes = int(raw_input('Please enter the number of wiimotes to set up'))
#control.addWiimotes(nummotes)
control.WiimoteGui()
print 'Wii Event Parser is set up. to quit, enter q'

exit = 0
while not exit:
	c = sys.stdin.read(1)
	if c == 'q':
		control.end()
		exit = 1	
