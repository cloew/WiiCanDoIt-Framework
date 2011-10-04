import sys,os

try:
	import ButtonControl
except:
	filepath = os.path.dirname(os.path.abspath(__file__))
	sys.path.append(os.path.dirname(filepath) + '/WiiEventParser')
	import ButtonControl	

buttonSet = ButtonControl.ButtonControl()

newButtons = 2047 
print 'TESTING NEW BUTTON PRESSES'

buttonSet.testEvent(0,newButtons,100)

newButtons = 0
print 'TESTING BUTTON RELEASES'

buttonSet.testEvent(0,newButtons,105)
