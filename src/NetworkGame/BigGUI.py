import os, sys, pygame, WIIGUIToolkit
from pygame.locals import *

from WIIGUIToolkit import *		   
from MainScreenGUI import *
import GUIObjects
from MapSelectionScreen import *

pygame.init()

videoInfo = pygame.display.Info()
SCALED_FULL_SCREEN = (videoInfo.current_w, videoInfo.current_h)
FULL_SCREEN_SIZE = (1024, 768)
CLOCK_TICKER = 40

class GMap:
	"""This class sets up the screen and manages which game screens
	are called when.  It's the big display that interfaces with the
	main menu, player role selection, level selection, and game
	screens.  There is the potential for a game over screen, but
	that is yet to be seen."""

	def __init__(self, game = None):
		"""This function initializes the map.  Fullscreen code above
		borrowed from the Binary Tree Game.  The default map is blank,
		and is blitted to depending on what screen is to be displayed."""

		self.screen = pygame.display.set_mode(FULL_SCREEN_SIZE)		   
		self.screen = self.screen.copy()
		self.window = pygame.display.set_mode(SCALED_FULL_SCREEN)

		self.cursor = GUIObjects.Hand(200, 200)
	
		self.allsprites = pygame.sprite.LayeredUpdates(self.cursor)
	
		pygame.display.set_caption('Network Game')
		self.background = pygame.Surface(self.screen.get_size())
		self.background = self.background.convert()
		self.background.fill(colors['WHITE'])
		self.screen.set_colorkey(colors['CKEY'])
		self.displaying = None

		self.game = game

	def run(self):
                """ This function draws the screen to the window including all the sprites
                Also, allows user input and interaction with a Screen.
                This function runs until either the screen stops running or the 
                game is exited """
		global CLOCK_TICKER

		running = 1

		clock = pygame.time.Clock()
		pygame.mouse.set_visible(0)

		while running:
			clock.tick(CLOCK_TICKER)

			# Collect user keyboard/mouse input
			self.getInput(pygame.event.get())

			# Update the sprites
			if hasattr(self.displaying, "update"):
				# If the screen wants to handle it
				self.displaying.update()
			else:
				# Otherwise, just update the sprites
				self.allsprites.update()
			
			# Blit the background and Screen Surface	
			self.screen.blit(self.background, (0, 0))
			self.screen.blit(self.displaying.surface, (0, 0))

			# Draw the sprites
			if hasattr(self.displaying, "draw"):
				# If the screen wants to handle it
				self.displaying.draw()
			else:
				# Otherwise, just draw the sprites
				self.allsprites.draw(self.screen)			
			
			# Now scale the surface if we need to		
			if FULL_SCREEN_SIZE == SCALED_FULL_SCREEN:
				self.window = self.screen
			else:
				self.window = self.scaleSurface( self.screen )
			

			pygame.display.flip()

			# Check if the screen is controlling how long it runs
			if hasattr(self.displaying, "running"):
				# If so, update accordingly
				running = self.displaying.running

	def scaleSurface(self, surface):
		""" Scales this objects window size to match 
                the size of the actual screen it's on """
		scaledSurface = pygame.transform.smoothscale(surface, SCALED_FULL_SCREEN, self.window)
		return scaledSurface

	def runScreen(self, newScreen):
		""" This function tells the GUI to display a particular 
                "Screen" sent in as a parameter. This screen is merely 
                a class that contains a Pygame surface with the layout
                of an interactive display. This function also collects
                the screen's sprites and any clickable items and adds
                them to this object so it can interact appropriately """
		self.displaying = newScreen
		
		# If the screen has sprites, collect them so they can be drawn from here
		if hasattr(newScreen, "allsprites"):
			self.allsprites = pygame.sprite.LayeredUpdates(newScreen.allsprites, self.cursor)

		# If the screen has items that need to be clicked, collect them so they can be clicked from here
		if hasattr(newScreen, "clickables"):
			self.clickables = newScreen.clickables

		self.run()

	""" Checks keyboard/mouse input for possible actions """
	"""   This class solely searches for exiting and mouse clicks """
	""" But, also calls the displaying screen to check its input """
	def getInput(self, events):
		for event in events:
			if event.type == QUIT:
				sys.exit(0)
			elif event.type == KEYDOWN and event.key == K_ESCAPE:
				sys.exit(0)
			elif event.type == MOUSEBUTTONDOWN:
				self.cursor.click(self.clickables)
			elif event.type == MOUSEMOTION:
				self.remapCursor(self.cursor)
			
			if hasattr(self.displaying, "getInput"):
				self.displaying.getInput([event])

	def remapCursor(self, hand):
		""" Remaps the cursor so it moves and interacts
                appropriately when the screen has been scaled """

		pos = pygame.mouse.get_pos()
		newX = pos[0] * (FULL_SCREEN_SIZE[0]/float(SCALED_FULL_SCREEN[0]))
		newY = pos[1] * (FULL_SCREEN_SIZE[1]/float(SCALED_FULL_SCREEN[1]))
		hand.x = newX
		hand.y = newY
