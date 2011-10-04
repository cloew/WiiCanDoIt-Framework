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
