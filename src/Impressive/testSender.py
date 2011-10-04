import socket

sendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sendSocket.sendto( 'next', ('localhost', 34567))
