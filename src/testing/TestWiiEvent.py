import sys,os
try:
	import WiiEvent
except:
	filepath = os.path.dirname(os.path.abspath(__file__))
	sys.path.append(os.path.dirname(filepath) + '/WiiEventParser')
	import WiiEvent

testEvent = WiiEvent.WiiEvent(11223,"pressA",-1)

print 'New Wii Event containing:\n'
print 'WiiMote ID:', testEvent.wiimoteID
print 'Action:', testEvent.action
print 'modifier:', str(testEvent.modifier)

print 'TESTING EVENT COMPRESSION'
eventstring = testEvent.compressEvent()
print eventstring

print 'TESTING EVENT DECOMPRESSION'
newTestEvent = WiiEvent.WiiEvent()
print 'default values: '
print 'Wiimote ID:', newTestEvent.wiimoteID
print 'Action:',newTestEvent.action
print 'modifier',newTestEvent.modifier

print 'decompressed Event Values:'
newTestEvent.deCompressEvent(eventstring)
print 'WiimoteID:', newTestEvent.wiimoteID
print 'action:', newTestEvent.action
print 'modifier:', newTestEvent.modifier
