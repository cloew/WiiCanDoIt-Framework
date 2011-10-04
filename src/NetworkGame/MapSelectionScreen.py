import pygame
import sys, os
import GUIObjects
from Tkinter import *
from pygame.locals import *
sys.path.append( os.path.dirname(os.path.abspath(os.path.dirname(__file__)))+'/WiiEventParser')
import GUINumberWiimotes
from BigGUI import FULL_SCREEN_SIZE
import Levels
from Globals import *
from WIIGUIToolkit import *

SCREEN_SIZE = FULL_SCREEN_SIZE

HEADER = (9,34,106)
TO_CHOOSE = (255,185,34)
SELECTED = (28,154,178)
BACKGROUND = (235,240,255)

class PlayerLight(pygame.sprite.Sprite):
	def __init__(self, x, y, playerNum):
		self.fileName = 'player' + str(playerNum+1) + '.png'
		pygame.sprite.Sprite.__init__(self)
		self.lightimage, self.lightrect = GUIObjects.load_image_alpha(self.fileName)
		self.rect = pygame.Rect(self.lightrect)
		self.rect.height += 75
		self.image = pygame.Surface((self.rect.width, self.rect.height))
		self.rect.centerx = x
		self.rect.centery = y
		self.playerNum = playerNum
		self.drawImage()	
		
	def update(self):
		pass

	def drawImage(self):
		self.image.fill(BACKGROUND)
		# First draw the circle
		circlePos = (self.rect.width/2, self.rect.height/2)
		color = COLORLIST[self.playerNum]
		color = colors[color]
		pygame.draw.circle(self.image, color, circlePos, 25)
		self.lightrect.top = self.rect.height - self.lightrect.height
		self.image.blit( self.lightimage, self.lightrect )
	

class MapSelection:
	def __init__(self, game = None):
		# Create all necessary variables
		self.headerFont = pygame.font.SysFont('Verdana', 40)
		self.font = pygame.font.SysFont('Verdana', 30)
		
		self.surface = pygame.Surface(SCREEN_SIZE)
		
		self.game = game
		self.running = 1

		self.numPlayers = self.game.numPlayers
		if self.numPlayers == 0:
			self.numPlayers = self.numPlayersGUI()

		self.playerLights = []
		self.addPlayerLights()	
		print "Running MapSelection"

		self.level1button = None
		self.level2button = None
		self.level3button = None
		self.level4button = None
		self.addLevelButtons()	

		self.clickables = [self.level1button, self.level2button, self.level3button, self.level4button]	  
		self.allsprites = pygame.sprite.LayeredUpdates( (self.playerLights, self.clickables))	  

		# Build the Screen and add the sprites
		self.buildScreen()
		#self.allsprites = []


	def addPlayerLights(self):
		# First figure out how many players there are
		gui = self.game.gui
		screenRect = gui.screen.get_rect()
		x = 100
		y = screenRect.height - 175 
		xoffset = 120
		print self.numPlayers
		for player in range(self.numPlayers):
			self.playerLights.append( PlayerLight( x, y, player) )
			x += xoffset

	def addLevelButtons(self):
		x = 150
		y = 50
		self.level1button = GUIObjects.ImageButton( (x, y), "level1.png", self.startLevel1)
		x = 400
		self.level2button = GUIObjects.ImageButton( (x, y), "level2.png", self.startLevel2)
		x = 150
		y = 250
		self.level3button = GUIObjects.ImageButton( (x, y), "level3.png", self.startLevel3)
		x = 400
		self.level4button = GUIObjects.ImageButton( (x, y), "level4.png", self.startLevel4)
		

	def startLevel1(self):
		print "Tryint to start level 1"
		self.game.mapOn = Levels.Level_1()
		self.game.startGame(self.numPlayers)

	def startLevel2(self):
		self.game.mapOn = Levels.Level_2()
		self.game.startGame(self.numPlayers)

	def startLevel3(self):
		self.game.mapOn = Levels.Level_3()
		self.game.startGame(self.numPlayers)

	def startLevel4(self):
		self.game.mapOn = Levels.Level_4()
		self.game.startGame(self.numPlayers)

	def numPlayersGUI(self):
		# Pop up a simple GUI that asks how many players to use
		w = 300
		h = 100
		root = Tk()
		root.title('Number of Players')
		app = GUINumberWiimotes.GUINumberWiimotes(root, "How many players?")
		screenWidth = root.winfo_screenwidth()
		screenHeight = root.winfo_screenheight()
		x = (screenWidth - w)/2
		y = (screenHeight - h)/2
		root.geometry('%dx%d+%d+%d' %(w, h, x, y))
		root.mainloop()
		root.withdraw()
		root.destroy()
		numMotes = app.numberWiimotes
		print "GUI num Motes", numMotes
		return numMotes


	def buildScreen(self):
		global BACKGROUND, HEADER, SELECTED, TO_CHOOSE
		
		# Build the text for the buttons
		self.surface.fill(BACKGROUND)
		# If given a header and team names
