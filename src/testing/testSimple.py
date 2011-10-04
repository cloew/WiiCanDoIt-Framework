import sys, os, time

try:
	import WiiEvent
except:
	filepath = os.path.dirname(os.path.abspath(__file__))
	sys.path.append(os.path.dirname(filepath))
	sys.path.append(os.path.dirname(filepath)+"/WiiEventParser")
	import WiiEvent

from bindings import *
from testGame import *
import socket
import time
import pickle
from threading import Thread

game = TestGame()
bindings = SampleGameEvents(game, 1)

f = open('testLogs/log00_multiple_bindings.txt', 'rb')
while 1:
	try:
		loadedWiiEvent = pickle.load(f)
		bindings.receiveWii( loadedWiiEvent.compressEvent() )
	except EOFError:
		break;
		print "End of file"
f.close()
