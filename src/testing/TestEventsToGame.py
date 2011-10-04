import socket
import pickle

theSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
theSocket.bind( ('localhost',37177) )	
while True:
	event,location = theSocket.recvfrom(1024)
	try:
		unpickled = pickle.loads(event)
		print unpickled 
	except:
		print 'Event:', event

