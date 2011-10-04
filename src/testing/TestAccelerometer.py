import sys, os

try:
	import Accelerometer
except:
	filepath = os.path.dirname(os.path.abspath(__file__))
	sys.path.append(os.path.dirname(filepath) + '/WiiEventParser')
	import Accelerometer

print 'THIS TEST IS OUT OF DATE, ACCELERATION MAGNITUDE IS NOT TESTED'
acc = Accelerometer.Accelerometer()

print 'TESTING ALL POSITIVE ACC THRESHOLDS'
acc.testEvent(1,0,275,275,275)

print 'TESTING TIME DELTA, NO EVENTS SHOULD TRIGGER'
acc.testEvent(1.1,0,70,70,70)

print 'TESTING ALL NEGATIVE ACC THRESHOLDS'
acc.testEvent(2,0,-100,-100,-100)

print 'TESTING NEG X, POS Y, NO Z'
acc.testEvent(2.5,0,-100,100,0)
