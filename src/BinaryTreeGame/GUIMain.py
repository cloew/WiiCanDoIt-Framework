import sys, os
import pygame

from pygame.locals import *

from GUIObjects import *
from MainScreenGUI import *

SCREEN_SIZE = (1152, 864) #(1024, 768)
FULL_SCREEN_SIZE = None

HEADER = (9, 34, 106)
BACKGROUND = (235, 240, 255)

CLOCK_TICKER = 40#120

""" The controlling class for all GUI interaction """
""" Builds the actual graphical window """
""" Holds a screen which builds the actual layout on the window """
""" Keeps track of the cursor sprite """
""" Keeps track of all sprites and draws them on the screen """
""" Keeps track of all items taht can be clicked by the cursor """
class GUIMain:
	""" Initializes the GUIMain object to have a screen that  """
	""" is scaled to fit the entire screen """
	""" Builds the cursor and builds a background """
	def __init__(self, theGame):
		global BACKGROUND
		
		self.game = theGame
		
		pygame.init()
		# Get the size of the display
		videoInfo = pygame.display.Info()
		self.FULL_SCREEN_SIZE = (videoInfo.current_w, videoInfo.current_h)		

		self.fullWindow = pygame.display.set_mode(SCREEN_SIZE) 
		self.fullWindow = self.fullWindow.copy()
		self.window = pygame.display.set_mode(self.FULL_SCREEN_SIZE)
		
		pygame.display.set_caption('Wii Tree Kings')
		pygame.mouse.set_visible(0)
		
		""" Build the Background """ # Will move to its own function
		background = pygame.Surface(self.fullWindow.get_size())
		self.background = background.convert()
		self.background.fill(BACKGROUND)
		
		""" Build the cursor """
		self.cursor = GUIObjects.Hand(200, 200)
		
		""" List of all things the cursor can click """
		self.clickables = None
		
		self.allsprites = pygame.sprite.LayeredUpdates(self.cursor)
		
		self.screen = None
		
		self.currentPlayer = 0
		self.fakeIns = {}
		
	""" Function that runs a loop to allow user input and refresh the screen """
	def run(self):
		global CLOCK_TICKER
		
		clock = pygame.time.Clock()
		running = 1

		while(running):
			clock.tick(CLOCK_TICKER)
			
			# Get user input
			self.getInput(pygame.event.get())
			
			# Update the cursor and all the screen's sprites
			self.allsprites.update()

			# Draw the Default background and the screen
			self.fullWindow.blit(self.background, (0, 0))
			self.fullWindow.blit(self.screen.surface, (0, 0))

			# Draw cursor and all the screen's sprites
			self.allsprites.draw(self.fullWindow)
		
			# Maximize the window if neccessary, so that it matches any resolution
			if self.FULL_SCREEN_SIZE == SCREEN_SIZE:
				self.window = self.fullWindow
			else:	
				self.window = self.scaleSurface( self.fullWindow )

			# Redraw the screen
			pygame.display.flip()
			
			# If the screen controls how long it runs
			if hasattr(self.screen, "running") :
				running = self.screen.running
		
	""" Change the screen then call the run function above """		  
	def runScreen(self, newScreen):
		# Set the new screen
		self.screen = newScreen
		
		# If that screen has sprites add them to the GUIMain object's allsprites
		if hasattr(newScreen, "allsprites") :
			self.allsprites = pygame.sprite.LayeredUpdates(newScreen.allsprites, self.cursor)
		
		# If that screen has items that can be clicked add them to the screen's clickables
		if hasattr(newScreen, "clickables") :
			self.clickables = newScreen.clickables
	
		# Run the screen	
		self.run()

	""" Function to scale the surface to the size of the screen """
	def scaleSurface( self, surface ) :
		scaledSurface = pygame.transform.smoothscale(surface, self.FULL_SCREEN_SIZE, self.window)
		return scaledSurface 		

	""" Function that remaps the cursor when the screen """ 
	""" gets stretched so it moves appropriately        """
	def remapCursor(self, hand):
		pos = pygame.mouse.get_pos()
		newX = pos[0] * (SCREEN_SIZE[0]/float(self.FULL_SCREEN_SIZE[0]))
		newY = pos[1] * (SCREEN_SIZE[1]/float(self.FULL_SCREEN_SIZE[1])) 
		hand.x = newX
		hand.y = newY
		pos = pygame.mouse.get_pos()

	""" Loop that gathers input from the user's mouse/keyboard  """
	""" Also, checks the GUIMain object's screen if it needs to """
	"""  do anything with the input                             """
	def getInput(self, events): 
		for event in events:
			# Exit if window closes 
			if event.type == QUIT: 
				sys.exit(0)
			# Exit if escape key is pressed
			elif event.type == KEYDOWN and event.key == K_ESCAPE:
				sys.exit(0)
			# Check if cursor clicks anything
			elif event.type == MOUSEBUTTONDOWN:
				self.cursor.click(self.clickables)
			# Unclick the cursor """
			elif event.type == MOUSEBUTTONUP:
				self.cursor.unclick()	
			elif event.type == MOUSEMOTION:
				# Since the screen is scaled, 
				# we have to remap the cursor position
				self.remapCursor(self.cursor)
			elif event.type == KEYDOWN:
				if event.key == K_s:
					print "doing", event.key
					self.fakeIns['flickx'] = -100
					self.fakeIns['flickz'] = 0
					self.fakeIns['player'] = self.currentPlayer
					self.game.tryShove(self.fakeIns)
				elif event.key == K_f:
					print "doing", event.key
					self.fakeIns['flickx'] = 100
					self.fakeIns['flickz'] = 0
					self.fakeIns['player'] = self.currentPlayer
					self.game.tryShove(self.fakeIns)
				elif event.key == K_e:
					print "doing", event.key
					self.fakeIns['flickx'] = 0
					self.fakeIns['flickz'] = 100
					self.fakeIns['player'] = self.currentPlayer
					self.game.tryShove(self.fakeIns)
				elif event.key == K_v:
					print "doing", event.key
					self.fakeIns['player'] = self.currentPlayer
					self.game.trySelect(self.fakeIns)
				elif event.key == K_z:
					print "doing", event.key
					self.fakeIns['player'] = self.currentPlayer
					self.game.tryDeselect(self.fakeIns)
				elif event.key == K_r:
					print "doing", event.key
					self.fakeIns['player'] = self.currentPlayer
					self.fakeIns['roll'] = -3
					self.game.tryRotate(self.fakeIns)
				elif event.key == K_t:
					print "doing", event.key
					self.fakeIns['player'] = self.currentPlayer
					self.fakeIns['roll'] = 3
					self.game.tryRotate(self.fakeIns)
					
				elif event.key == K_o:
					print "doing", event.key
					if self.currentPlayer > 0:
						self.currentPlayer -= 1
				elif event.key == K_p:
					print "doing", event.key
					if self.currentPlayer < 5:
						self.currentPlayer += 1
				elif event.key == K_j:
					self.game.playerOn = 0
					self.game.addPlayerA(dict([('player', 0)]))
					self.game.addPlayerB(dict([('player', 3)]))
				elif event.key == K_k:
					self.game.playerOn = 1
					self.game.addPlayerA(dict([('player', 1)]))
					self.game.addPlayerB(dict([('player', 4)]))
				elif event.key == K_l:
					self.game.playerOn = 2
					self.game.addPlayerA(dict([('player', 2)]))
					self.game.addPlayerB(dict([('player', 5)]))
					

			# Check if screen is looking for input events
			if hasattr(self.screen, "getInput") :
				result = self.screen.getInput([event])
				# Check if the input tells to exit the current game
				if result == "exit":
					self.game.endGame()
		
	
