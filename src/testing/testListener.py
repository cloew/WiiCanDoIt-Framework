#load our custom bindings file
from bindings import *
# load the socket module
from socket import *
import sys


#load our test game
from testGame import *

game = TestGame()

bindings = SampleGameEvents(game, 4)

bindings.start( )

running = True
while running:
	input = raw_input()
	input = input.strip()
	if( input == 'q'):
		running = False
		bindings.end()
