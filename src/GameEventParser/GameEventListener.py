import os, sys, select, subprocess, signal
import GameEventLogger
import socket
import pickle
from threading import Thread

try:
	import ParserSettings
except:
	filepath = os.path.dirname(os.path.abspath(__file__))
	sys.path.append(os.path.dirname(filepath))
	import ParserSettings

class GameEventListener(Thread):
	def __init__(self, game, bindingsFile, bindingsClass, numPlayers):
		Thread.__init__(self)
		self._serversocket = None
		self._game = game
		self._bindingsFile = bindingsFile
		self._bindingsClass = bindingsClass
		self._numPlayers = numPlayers

	def run(self):
		# Spawn all the processes for the other parsers
		self.GEPpid = subprocess.Popen(['python', '../GameEventParser/startGEP.py', self._bindingsFile, self._bindingsClass, str(self._numPlayers)], stdin=subprocess.PIPE)
		self.WEPpid = subprocess.Popen(['python', '../WiiEventParser/startWEP.py'], stdin=subprocess.PIPE)
		
		# Start this socket listening
		self._serversocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self._serversocket.bind( (ParserSettings.GAME_HOST, ParserSettings.GAME_PORT) )
		self.listen()

	def join (self, timeout = None):
		self.running = 0
		Thread.join(self,timeout)

	def listen(self):
		input = [self._serversocket, sys.stdin]
		self.running = 1
		while self.running:
			inputready, outputready, execptready = select.select(input, [], [])
			for s in inputready:
				if s == self._serversocket:
					receivedEvent, location = self._serversocket.recvfrom(1024)
					if receivedEvent == 'q':
						self.running = 0
						break
					self.callGameFunc(receivedEvent)
				elif s == sys.stdin:
					junk = sys.stdin.readline()
					self.running = 0	
				if self.running == 0:
					break
		self._serversocket.close()


	def callGameFunc(self, receivedEvent) :
		funcParams = pickle.loads(receivedEvent)
		func, params = funcParams
		func = func[ParserSettings.GEP_BIND_PREFIX_LEN:]
		callback = getattr(self._game, func)
		if callable(callback):
			callback(params)	

	def end(self):
		print "Ending the Wiimote framework"
		self.running = 0
		self.WEPpid.communicate('q')
		self.GEPpid.communicate('q')
		try:
			os.kill(self.WEPpid.pid, signal.SIGKILL)
			os.kill(self.GEPpid.pid, signal.SIGKILL)
			return
		except:
			print sys.exc_info()[1]
		try:
			self.WEPpid.kill()
			self.GEPpid.kill()
			return
		except:
			print sys.exc_info()[1]
		killSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		killSocket.sendto('q',(ParserSettings.GAME_HOST,ParserSettings.GAME_PORT))
