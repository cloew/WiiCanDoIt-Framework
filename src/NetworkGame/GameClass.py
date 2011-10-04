
from threading import Timer
from random import *
import sys,os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from GameEventParser.GameEventCore import *
from GameEventParser.GameEventListener import *
from WiiEventParser.WEPControl import *

from PlayerClass import *
from MapClass import *
from BindingsClass import *
from Globals import COLORLIST
from BigGUI import *
from MainScreenGUI import *

""" This class holds mostly game variables and functions to carry wiimote input """
"""   through to the actual game logic in the Map Class                         """
class Game:
	def __init__(self):
	    # Game's map variable	  
	    # Initialized to none since not actually playing when game is loaded
	    # Also, should be the only map object at all in the game
	    self.mapOn = "None"
		
            # Game's variables to keep track of players
	    self.numPlayers = 0
	    self.playerList = ([])

	    self.gui = None

	def buildGUI(self):
	    self.gui = GMap(self)
	    self.gui.runScreen(MainScreen(self))

	def getMap(self):
		return self.mapOn

	def setMap(self, newMap):
		self.mapOn = newMap

	""" Return the playerList """
	def getPlayerList(self):
		return self.playerList

	""" Return a player by index """
	def getPlayer(self, index):
		return self.playerList[index]

	""" Adds a player to the Player List and assigns their color """
	def addPlayer(self):
            global COLORLIST

	    self.playerList.append(Player(self.numPlayers, COLORLIST[self.numPlayers]))
	    self.numPlayers += 1
	
	""" Find a Player with a specific wiiID and return 'their' node """
	"""   if applicable												"""
	def searchPlayers(self, inID):
		for player in self.playerList :
			if player.wiiID == inID :
				return self.mapOn.findNode(player.color)

	""" Removes all players """
	def clearPlayers(self):
		self.playerList = ([])
		self.numPlayers = 0

	""" Function called when a wiimote is flicked	"""
	""" Sees if it was a player who did the action	"""
	""" Then tries to send a packet from their node """
	def filterInput(self, params):
		# Check if the player is playing(aka does the player's color match the color of a node on the map
		wiiID = params['player']
		node = self.searchPlayers(wiiID)

		# If the player isn't controlling a node, return
		if not node:
			return

		# Normalize the flicks
		theX = params['flickx']
		theY = params['flickz']
		
		if theX > 0 :
			x = 1
		elif theX < 0 :
			x = -1
		else:
			x = 0

		if theY > 0 :
			y = 1
		elif theY < 0 :
			y = -1
		else:
			y = 0

		# And try to send
		self.mapOn.trySend(node, x, y)

	""" Function that initializes the Game Event Parser to start sending events """
	def startGame(self, numPlayers = 0):
		# Add Player objects to the game for every human player
		for x in range(numPlayers) :
			self.addPlayer()

		# If there are human players, start the Game Listener so Wiimotes can be used
		if numPlayers > 0:
                    self.listener = GameEventListener(self,'BindingsClass.py','Bindings', numPlayers)
                    self.listener.start()

		# Set up G\the Maps Variables and tell the Map to start play by adding Packets
		self.mapOn.numPlayers = numPlayers
		self.mapOn.setPacketTimer() 
		self.gui.runScreen(self.mapOn.mapScreen) 

	""" Function that ends the Game listener if it needs to be """
	def endGame(self):
            if self.numPlayers > 0:
                self.listener.end()
