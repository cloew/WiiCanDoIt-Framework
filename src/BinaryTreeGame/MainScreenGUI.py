import sys, os, signal
import pygame
import subprocess

from pygame.locals import *
import GUIObjects

try:
	from WiiEventParser.WEPControl import * 
except:
	location = os.path.dirname(os.path.abspath(__file__))
	sys.path.append(os.path.dirname(location) + '/WiiEventParser')
	print sys.path
	from WEPControl import *

SCREEN_SIZE = (1024, 768)

HEADER = (9,34,106)
TO_CHOOSE = (255,185,34)
SELECTED = (28,154,178)
BACKGROUND = (235,240,255)


""" Builds the Main Menu Screen """
class MainScreen:
	def __init__(self, game):
		global HEADER, BACKGROUND
		
		self.surface = pygame.Surface(SCREEN_SIZE)
		self.game = game
		
		self.surface.fill(BACKGROUND)
	
		# Draw the logo	
		self.logo, self.logoRect = GUIObjects.load_image_alpha('wiiTreeKings.png')
		rect = self.surface.get_rect()
		logoPos = ((rect.width-self.logoRect.width)/2, 120)
		self.surface.blit( self.logo, logoPos )		

		self.WEPControl = None
		
		pygame.display.flip()
		
		# Build the Buttons
		addButton = GUIObjects.Button((self.surface.get_rect().centerx - 250, 600), "Add Wiimotes", self.addWiimotes)
		exitButton = GUIObjects.Button((self.surface.get_rect().centerx, 700), "Exit", sys.exit)
		playButton = GUIObjects.Button((self.surface.get_rect().centerx + 250, 600), "Play the Game", self.buildTwoGame)
		
		# Make the Buttons clickable on the window and part of the allsprites for the window
		self.clickables = [addButton, exitButton, playButton]
		self.allsprites = pygame.sprite.LayeredUpdates((addButton, exitButton, playButton))

		self.WEPControlpid = None

	""" Destroy the WEPControl if there is one """
	def __del__(self):
		if not self.WEPControl == None:
			os.kill( self.WEPControlpid, signal.SIGKILL)
	
	""" Start the Two Team Versus Mode """
	def buildTwoGame(self):
		from TwoTeamVersusModeClass import *
		self.game = TwoTeamVersusMode()
		self.game.startGame()
	
	""" Begin the WEPControl, so that Wiimotes can be added """	
	def addWiimotes(self):
		self.WEPControlpid = subprocess.Popen(['python', '../WiiEventParser/startWEPControl.py'])
	
