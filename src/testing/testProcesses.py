import os
import sys
import subprocess

sys.path.append( os.path.abspath(os.path.dirname("../" +os.path.dirname(__file__))))
from GameEventParser import GameEventListener
from WiiEventParser import WEPControl
import bindings
import testGame

numPlayers = 4
game = testGame.TestGame()

listener = GameEventListener.GameEventListener(game, 'bindings.py', 'SampleGameEvents', 4)

listener.start()
