
from random import *
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from GameEventParser.GameEventCore import *
from WiiEventParser.WEPControl import *
from GameEventParser.GameEventListener import *

from GameModeClass import GameMode
from Bindings import *
from PlayerClasses import *
from TeamClass import Team

from PlayerSelectionScreen import *
from TwoTeamVersusScreen import *

""" Controlling Class for the Two Team Versus Mode """
class TwoTeamVersusMode(GameMode):
	""" Builds the object to be a basic uninitialized TwoTeamVersusMode """
	def __init__(self):
		# Parents constructor
		GameMode.__init__(self)

		# Build default or empty versions of all variables
		self.teams = []
		self.playing = 0
		self.order = ["Sorter", "Inserter", "Rotator"]
		
		self.playerOn = 0

	def __del__(self):
		try:
			self.listener.end()
			self.listener.join()
		except:
			pass
			# Listener wasn't started
	
	""" Called when the game is over """
	def gameOver(self, team):
		# Find the team that won
		for x in self.teams :
			if x is team :
				# Stop playing and tell the team they won
				self.playing = 0
				index = self.teams.index(team)
				self.getScreen().drawWinner(index)

	""" Turns off the Game Listener and returns to the Main Screen"""
	def endGame(self):
		self.listener.end()
		self.returnToMain()

	""" Tells the GUI to update the Screen since the tree is now balanced """
	def itsBalanced(self, team):
		index = self.teams.index(team)
		self.getScreen().itsBalanced(index)
		
	""" Returns a player based on wiiID            """
	""" Returns None if that player is not playing """
	def findPlayer(self, wiiID):
		for team in self.teams :
			for player in team.playerList :
				if player.wiiID == wiiID :
					return player
		return None
	
	""" Begins the Game by Prompting for players and then running the Game Screen """
	def startGame(self):
		self.getPlayers()
		self.playing = 1
		self.GUI.runScreen(TwoTeamVersusGameScreen(self.teams))
	
	""" Build and run the Proimpt screen until all Roles are filled """	
	def getPlayers(self):
		input1 = "Red"
		input2 = "Blue"

		teamA = Team(input1, self)
		teamB = Team(input2, self)

		self.teams.append(teamA)
		self.teams.append(teamB)

		# Set up Bindings for picking players and playing the Game
		self.listener = GameEventListener(self,'Bindings.py','PlayerSelectionBindings', 6)
		self.listener.start()
		
		# While loop to wait for all players to be selected
		while self.playerOn < 3 :
			# Prompt for self.order[self.playerOn]
			thePrompt = self.order[self.playerOn] + "s"
			
			# Building player selection screen for the Player Role needed
			self.GUI.runScreen(PlayerSelection([input1, input2], thePrompt))
		
			# Get the next type of player
			self.playerOn += 1
	
	""" Adds a player to TeamA """
	def addPlayerA(self, wiiInputs):
		# Check if playing, if you are can't add player
		if self.playing:
			return

		if self.getScreen().playerSelected[0]:
			return

		wiiID = wiiInputs['player']

		# Check if the player has already chosen a role
		player = self.findPlayer(wiiID)
		if player:
			return

		# Build theDict to contain all the values needed by the new Player
		theDict = {}
		theDict['player'] = wiiID
		theDict['team'] = self.teams[0]
		theDict['oppTeam'] = self.teams[1]
		
		# Add the appropriate player
		if self.playerOn == 0 :
			print "Adding Sorter"
			player = Sorter(theDict)
		elif self.playerOn == 1:
			print "Adding inserter"
			player = Inserter(theDict)
		elif self.playerOn == 2:
			print "Adding Rotator"
			player = Rotator(theDict)
		
		# Add the player to the first Team
		self.teams[0].addPlayer(player)
		# Tell the GUI that the player has picked
		self.GUI.screen.playerHasPicked(0)
	
	""" Adds a Player to TeamB """
	def addPlayerB(self, wiiInputs):
		# Check if playing, if you are can't add player
		if self.playing:
			return

		if self.getScreen().playerSelected[1]:
			return

		wiiID = wiiInputs['player']

		# Check if the player has already chosen a role
		player = self.findPlayer(wiiID)
		if player:
			return
		
		# Build theDict to contain all the values needed by the new Player
		theDict = {}
		theDict['player'] = wiiID
		theDict['team'] = self.teams[1]
		theDict['oppTeam'] = self.teams[0]
		
		# Add the appropriate player
		if self.playerOn == 0 :
			player = Sorter(theDict)
		elif self.playerOn == 1:
			player = Inserter(theDict)
		elif self.playerOn == 2:
			player = Rotator(theDict)
		
		# Add the player to Team B
		self.teams[1].addPlayer(player)
		# Tell the GUI that the player has picked
		self.GUI.screen.playerHasPicked(1)
	
	""" Tries to call a players shove function """
	def tryShove(self, wiiInputs):
		# If not playing, don't allow the game action
		if not self.playing:
			return

		# Get required data from the wiimote
		wiiID = wiiInputs['player']
		inX = wiiInputs['flickx']
		inY = wiiInputs['flickz']
		
		# Normalize the X and Y to 1, -1, or 0
		if inX > 0:
			x = 1
		elif inX < 0:
			x = -1
		else:
			x = 0
			
		if inY > 0:
			y = 1
		elif inY < 0:
			y = -1
		else:
			y = 0
		
		player = self.findPlayer(wiiID)
		
		# If the player is playing
		if player :
			# Call that player's shove function
			worked = player.shove((x, y))

			# Update the GUI based on the player's role			
			name = player.getName()
			
			if name == "Sorter" :
				# Update the queue appropriate GUI Queue
				index = self.teams.index(player.oppTeam)
				self.getScreen().moveInQueue(index, player.current)
					
			if name == "Inserter" :
				# Update the screen
				index = self.teams.index(player.team)
				self.getScreen().update(index)

			if name == "Rotator" :
				# Update the appropriate GUI Tree
				index = self.teams.index(player.team)
				self.getScreen().moveInTree(index, player.current)
	
	""" Tries to call a player's rotate function """	
	def tryRotate(self, wiiInputs):
		# If not playing, don't allow the game action
		if not self.playing:
			return

		# Get required data from the wiimote
		wiiID = wiiInputs['player']
		roll = wiiInputs['roll']

		player = self.findPlayer(wiiID)

		# If the player is playing
		if player :
			# Call that player's rotateB function
			worked = player.rotate(roll)

			# Update the GUI based on the player's role
			name = player.getName()

			if name == "Rotator" :
				# Update the appropriate GUI Tree
				index = self.teams.index(player.team)
				self.getScreen().rotateTree(index, player.current)
	
	""" Tries to call a player's select function """
	def trySelect(self, wiiInputs):
		# If not playing, don't allow the game action
		if not self.playing:
			return

		# Get required data from the wiimote
		wiiID = wiiInputs['player']
		
		player = self.findPlayer(wiiID)
		
		# If the player is playing
		if player :
			# Call that player's select function
			player.select()

			# Update the GUI based on the player's role
			name = player.getName()
			
			if name == "Sorter" :
				# Update the queue appropriate GUI Queue
				index = self.teams.index(player.oppTeam)
				self.getScreen().selectQueue(index)
			elif name == "Rotator" :
				# Update the appropriate GUI Tree
				index = self.teams.index(player.team)
				self.getScreen().selectTree(index)
	
	""" Tries to call a player's deselect function """
	def tryDeselect(self, wiiInputs):
		# If not playing, don't allow the game action
		if not self.playing:
			return
		
		# Get required data from the wiimote
		wiiID = wiiInputs['player']
		
		# If the player is playing
		player = self.findPlayer(wiiID)
		
		if player :
			player.deselect()

			# Update the GUI based on the player's role
			name = player.getName()
			
			if name == "Sorter" :
				# Update the queue appropriate GUI Queue
				index = self.teams.index(player.oppTeam)
				self.getScreen().deselectQueue(index)
			elif name == "Rotator" :
				# Update the appropriate GUI Tree
				index = self.teams.index(player.team)
				self.getScreen().deselectTree(index)
