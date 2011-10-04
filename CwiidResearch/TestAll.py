import cwiid
import WiimotePairing
import sys

X_UPPER = 200
X_LOWER = 50
Y_UPPER = 200
Y_LOWER = 50
Z_UPPER = 200
Z_LOWER = 50

def main():
	wiimote = WiimotePairing.PairWiimote()
	
	report_mode = 0
	report_mode ^= cwiid.RPT_BTN
	report_mode ^= cwiid.RPT_ACC

	wiimote.rpt_mode = report_mode

	wiimote.mesg_callback = callback

	print 'The wiimote is now set up. to exit press 0'

	exit = 0
	while not exit:
		c = sys.stdin.read(1)
		if c == '0':
			exit = 1

def callback(mesg_list, time):
	for message in mesg_list:
		if message[0] == cwiid.MESG_BTN:
			print 'TIME:', time
			print 'HEX BUTTON CMD:',hex(message[1])
		elif message[0] == cwiid.MESG_ACC:
			testFlickEvent(message[1][cwiid.X],message[1][cwiid.Y],message[1][cwiid.Z])

def testFlickEvent(x,y,z):
	if x > X_UPPER:
		print 'FLICKED TO THE LEFT'
	elif x < X_LOWER:
		print 'FLICKED TO THE RIGHT'
	if y > Y_UPPER:
		print 'FLICKED FORWARD'
	elif y < Y_LOWER:
		print 'FLICKED BACKWARD'
	if z > Z_UPPER:
		print 'FLICKED UP'
	elif z < Z_LOWER:
		print 'FLICKED DOWN'	

main()
