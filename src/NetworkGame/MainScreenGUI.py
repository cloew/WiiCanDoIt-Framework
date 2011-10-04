import sys, os, signal, WIIGUIToolkit
import pygame
import subprocess

from pygame.locals import *
from WIIGUIToolkit import *
import GUIObjects, Levels
from MapSelectionScreen import *

try:
	from WiiEventParser.WEPControl import * 
except:
	location = os.path.dirname(os.path.abspath(__file__))
	sys.path.append(os.path.dirname(location) + '/WiiEventParser')
	from WEPControl import *

pygame.init()
videoInfo = pygame.display.Info()
FULL_SCREEN_SIZE = (1152, 864)   

HEADER = (9,34,106)
TO_CHOOSE = (255,185,34)
SELECTED = (28,154,178)
BACKGROUND = (235,240,255)

class MainScreen:
	""" Builds the Main Screen for the Network Game """
	def __init__(self, game):
		""" Builds the Main Menu Screen so that it displays the 
		Title of the Game and adds all the buttons it needs """
		global HEADER, BACKGROUND
		
		self.surface = pygame.Surface(FULL_SCREEN_SIZE)
		self.game = game
		
		self.surface.fill(BACKGROUND)
		
		# Build the Title
		font = pygame.font.SysFont('Verdana', 104)
		text = font.render("Network Game", 1, HEADER)
		textpos = text.get_rect()
		
		textpos.centerx = self.surface.get_rect().centerx
		textpos.centery = self.surface.get_rect().centery - 200
		
		self.surface.blit(text, textpos)
		
		# Build the buttons
		addButton = GUIObjects.Button((self.surface.get_rect().centerx - 200, 500), "Add Wiimotes", self.addWiimotes)
		exitButton = GUIObjects.Button((self.surface.get_rect().centerx, 600), "Exit", sys.exit)
		playButton = GUIObjects.Button((self.surface.get_rect().centerx + 200, 500), "Play the Game", self.buildMapScreen)
		
		self.clickables = [addButton, exitButton, playButton]
		self.allsprites = pygame.sprite.LayeredUpdates((addButton, exitButton, playButton))
		self.numPlayers = None

	#def __del__(self):
		#if not self.WEPControl == None:
			#os.kill( self.WEPControlpid, signal.SIGKILL)
	
	def buildMapScreen(self):
		""" Tells the GUI to display the Map Selection Screen """
		gui = self.game.gui
		gui.runScreen(MapSelection(self.game))	

	def addWiimotes(self):
		""" Lets the players add Wiimotes """
		self.wepcontrol = WEPControl()	
		self.wepcontrol.WiimoteGui()
		self.numPlayers = self.wepcontrol._numMotes
