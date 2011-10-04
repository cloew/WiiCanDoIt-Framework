import cwiid

def PairWiimote():
	dummyVar = raw_input("Put the Wiimote you would like to use in discoverable mode the press ENTER:")

	print 'Pairing with wiimote:',
	wiimote = cwiid.Wiimote()
	print 'PASSED'

	print 'Enabling wiimote reporting:',
	wiimote.enable(cwiid.FLAG_MESG_IFC)
	print 'PASSED'

	return wiimote
