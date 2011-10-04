from socket import *
import pickle

HOST = 'localhost'
PORT = 76543
BUFSIZ = 1024
ADDR = (HOST, PORT)
serversock = socket(AF_INET, SOCK_DGRAM)
serversock.bind(('',PORT))

while 1:
		data, location = serversock.recvfrom(BUFSIZ)
		print 'data: ' + data
		item = pickle.loads(data)
		print item.wiimoteID,item.action,item.modifier
  
serversock.close()
