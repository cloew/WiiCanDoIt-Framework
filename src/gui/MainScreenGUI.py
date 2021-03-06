import sys, os, signal, WIIGUIToolkit
import pygame
import subprocess

from pygame.locals import *
from WIIGUIToolkit import *
import GUIObjects, Levels

try:
	from WiiEventParser.WEPControl import * 
except:
	location = os.path.dirname(os.path.abspath(__file__))
	sys.path.append(os.path.dirname(location) + '/WiiEventParser')
	print sys.path
	from WEPControl import *

pygame.init()
videoInfo = pygame.display.Info()
FULL_SCREEN_SIZE = (videoInfo.current_w, videoInfo.current_h)   

HEADER = (9,34,106)
TO_CHOOSE = (255,185,34)
SELECTED = (28,154,178)
BACKGROUND = (235,240,255)

class MainScreen:
	def __init__(self, game):
		global HEADER, BACKGROUND
		
		self.surface = pygame.Surface(FULL_SCREEN_SIZE)
		self.game = game
		
		self.surface.fill(BACKGROUND)
		
		font = pygame.font.SysFont('Verdana', 104)
		text = font.render("Network Game", 1, HEADER)
		textpos = text.get_rect()
		
		textpos.centerx = self.surface.get_rect().centerx
		textpos.centery = self.surface.get_rect().centery - 200
		
		self.surface.blit(text, textpos)
		
		addButton = GUIObjects.Button((self.surface.get_rect().centerx - 250, 600), "Add Wiimotes", self.addWiimotes)
		exitButton = GUIObjects.Button((self.surface.get_rect().centerx, 700), "Exit", sys.exit)
		playButton = GUIObjects.Button((self.surface.get_rect().centerx + 250, 600), "Play the Game", self.buildTestLevel)
		
		self.clickables = [addButton, exitButton, playButton]
		self.allsprites = pygame.sprite.LayeredUpdates((addButton, exitButton, playButton))
		#self.WEPControlpid = None

	#def __del__(self):
		#if not self.WEPControl == None:
			#os.kill( self.WEPControlpid, signal.SIGKILL)
	
	def buildTestLevel(self):
		self.game.mapOn = Levels.Big_Test_Level()
		self.game.startGame()
				
	def addWiimotes(self):
		self.wepcontrol = WEPControl()	
		self.wepcontrol.WiimoteGui(2)
"""	
#Main Loop
pygame.init()
clock = pygame.time.Clock()
window = pygame.display.set_mode(FULL_SCREEN_SIZE)
pygame.display.set_caption('Network Game')
pygame.mouse.set_visible(0)
while 1:
    clock.tick(60)
    screen = MainScreen()
    cursor = GUIObjects.Hand(200,200)    
    screen.allsprites.add(cursor)
    window.blit(screen.surface, (0,0))
    screen.allsprites.update()
    screen.allsprites.draw(window)
    
    screen.getInput(pygame.event.get())"""
