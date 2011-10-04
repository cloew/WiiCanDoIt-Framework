import pygame, sys, os
from pygame.locals import *

import threading

try:
	from WIIGUIToolkit import *
except:
	location = os.path.dirname(os.path.abspath(__file__))
	sys.path.append(os.path.dirname(location) + '/gui')
	from WIIGUIToolkit import *
	
#from TreeClass import node

OVERLAY_ALPHA = 50 
BACKGROUND = (235, 240, 255)

""" Load an image from a file, converts alpha for better appearance """
""" name: filename of the image                                     """
""" Returns a Pygame Surface with the image and a Pygame Rect set   """ 
"""  to the dimensions of the Surface                               """
def load_image_alpha(name):
	fullname = os.path.join('data', name)
	try:
		image = pygame.image.load(fullname)
	except pygame.error, message:
		print "Cannot load image:", name
		raise SystemExit, message
	image = image.convert_alpha()
	return image, image.get_rect()


""" This class creates a cursor that cahnges position """
"""   based on its x and y variables                  """
""" Used in place of the standard Mouse Cursor        """
class Hand(pygame.sprite.Sprite):
	""" Creates the Hand object by loading the image  """
	"""   and setting the x and y to the coords given """
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image, self.rect = load_image_alpha("handPoint.png")
		self.clicking = 0
		self.x = x
		self.y = y
	
	""" Moves the cursor's rect so that the Hand object will """
	"""   appear at its x and y coordinates                  """
	def update(self):
		pos = (self.x, self.y)
		self.rect.midtop = pos
		if self.clicking:
			self.rect.move_ip(5, 10)
	
	""" Check if the mouse button has clicked anything """
	def click(self, targets):
		# Set the Hand to clicking
		self.clicking = 1
				
		# If there's nothing to click, return
		if not targets :
			return
		
		# Check if anything got clicked
		hitbox = self.rect.inflate(-5, -5)
		for target in targets :
			if hitbox.colliderect(target) :
				target.clicked(hitbox.topleft)
	
	""" Resets the clicking bool to false """
	def unclick(self):
		self.clicking = 0

""" A Sprite that acts as a button and calls a function when clicked """
class Button(pygame.sprite.Sprite):
	""" Builds a Button object to appear at the given coords """
	""" Draws the provided text on a background color        """
	def __init__(self, coords, inText, func, overlayColor = None):
		pygame.sprite.Sprite.__init__(self)
		self.text = inText
		self.func = func
	
		self.textColor = (9, 34, 106)
		self.borderColor = (157, 182, 255)	
		self.overlayColor = overlayColor
		if self.overlayColor == (255, 0, 0):
			self.bgImage, self.bgImageRect = load_image_alpha("buttonBGRed.png")
		else:
			self.bgImage, self.bgImageRect = load_image_alpha("buttonBGBlue.png")

		self.x, self.y = coords
		self.rect = self.bgImageRect
	
		self.rect.centerx = self.x
		self.rect.centery = self.y
		
		self.surf = pygame.Surface((self.rect.width, self.rect.height))
		
		self.addText()

	""" Adds text to the Button's surface """
	def addText(self):
		font = pygame.font.SysFont('Verdana', 36)
		text = font.render(self.text, 1, self.textColor )
		textpos = text.get_rect()
		self.rect = textpos.inflate(20, 20)
		
		self.rect.centerx = self.x
		self.rect.centery = self.y
	
		self.surf = pygame.Surface((self.rect.width, self.rect.height))
		textpos.centerx = self.surf.get_rect().centerx
		textpos.centery = self.surf.get_rect().centery
		
		self.textStuff = (text, textpos)
	
	""" Draws the Background rectangle and redraws the text               """
	""" Then sets the image to be displayed equal to the Button's surface """
	def update(self):
		text, textpos = self.textStuff
		
		self.drawBGRect(textpos)
		if text is not None:
			self.surf.blit(text, textpos)
		
		self.image = self.surf

	""" Draws the background for the Button """
	def drawBGRect(self, textpos, alpha=254):
		# First draw the background to fill the entire rectangle
		bgWidth = self.bgImageRect.width
		x = 0
		while x < self.rect.width:
			self.surf.set_alpha(alpha)
			self.surf.blit(self.bgImage, (x, -10))
			x += bgWidth
		# Draw a bounding box
		boundingBox = textpos.inflate( 20, 20 )
		pygame.draw.rect(self.surf, self.borderColor, boundingBox, 1)	
		self.surf.set_alpha(254)	

	""" Calls the Button's function when clicked """
	def clicked(self, top_left):
		self.func()

class ImageButton(pygame.sprite.Sprite):
	def __init__(self, coords, image, func = None):
		pygame.sprite.Sprite.__init__(self)
		self.func = func	
		self.bgImage, self.rect = load_image_alpha(image)	
		self.rect.left = coords[0]
		self.rect.top = coords[1]
		
		self.image = pygame.Surface((self.rect.width, self.rect.height))
		rect = self.image.get_rect()
		print rect.width, rect.height

	def update(self):
		self.drawBGRect()

	def drawBGRect(self):
		blitPos = pygame.Rect(self.rect)
		blitPos.top = 0
		blitPos.left = 0

		self.image.blit(self.bgImage, blitPos)

	def clicked(self, top_left):
		self.func()

""" A Button that highlights and can't be clicked """
class PlayerSelectButton(Button):
	def __init__(self, coords, inText, func = None, overlayColor = None):
		Button.__init__(self, coords, inText, func, overlayColor)	

	""" Highlights the Button """
	def highlight(self):
		self.bgImage, self.bgImageRect = load_image_alpha('buttonBGSelected.png')	

	def clicked(self, top_left):
		# Don't do anything if it is clicked
		pass

""" A Button that fades out over time """
class StatusButton(Button):
	def __init__(self, coords, inText, func = None, overlayColor = None):
		global BACKGROUND

		Button.__init__(self, coords, inText, func, overlayColor)
		self.image = self.surf.fill(BACKGROUND)
		self.appear = 0
		self.alpha = 254
		self.fade = 1
	
	""" Sets the image to be drawn equal to the surf if it needs to be drawn """
	def update(self):
		global BACKGROUND
		
		self.surf.fill(BACKGROUND)

		if self.appear:
			text, textpos = self.textStuff
			self.drawBGRect(textpos, self.alpha)
			self.surf.set_alpha(self.alpha)
			self.surf.blit(text, textpos)

		self.image = self.surf
		
	def clicked(self, top_left):
		# Don't do anything if it is clicked
		pass
	
	""" Cause the Button to appear and slowly fade """
	def show(self):
		self.appear = 1
		self.alpha = 254
		self.setTimer()
		
	""" Build a Timer that causes the Button to fade a little """
	def setTimer(self):
		self.timer = threading.Timer(0.2, self.fadeOut)
		self.timer.start()
	
	""" Function to make the Button more and more see through until it disappears """
	def fadeOut(self):
		if self.fade:
			self.alpha = self.alpha - 30
			if self.alpha <= 0:
				self.alpha = 0
				self.appear = 0
			else:
				self.setTimer()
		else:
			self.alpha = 254

""" Displays a Timer That counts down from 3 """
class GUITimer(pygame.sprite.Sprite):
	def __init__(self, player, coords, overlayColor = (0, 0, 255)):
		pygame.sprite.Sprite.__init__(self)
		self.player = player
		self.overlayColor = overlayColor

		self.backgroundColor = (235, 240, 255)
		self.image = pygame.Surface( (50, 50) )
		self.rect = self.image.get_rect()
		self.rect.topleft = coords 
		self.timer = None		
		self.text = 3

		self.font = pygame.font.SysFont('Verdana', 36)

	""" Prints the timer numbers if its player has a timer going """
	def update(self):
		self.image.fill( self.backgroundColor )
		if self.player.timer != None:
			if self.timer == None:
				self.timer = threading.Timer(1.0, self.changeText)
				self.timer.start()
	
			text = self.font.render(str(self.text), 1, self.overlayColor )
			textpos = text.get_rect()
			self.image.blit(text, textpos)
		else:
			self.text = 3

	""" Changes the text the timer displays """
	def changeText(self):

		self.text = self.text - 1
		if self.text > 0 :
			self.timer = threading.Timer(1.0, self.changeText)
			self.timer.start()
		else:
			self.timer = None	

""" A Sprite that only displays an image """
""" this image is invisible at first     """
class ImageContainer(pygame.sprite.Sprite):
	def __init__(self, imageName, coord):
		global BACKGROUND
		
		pygame.sprite.Sprite.__init__(self)

		self.imageName = imageName
		self.surf, self.rect = load_image_alpha("crown.png")
		
		x, y = coord
		self.x = x
		self.y = y
		self.rect.centerx = x
		self.rect.centery = y
		
		self.image = pygame.Surface((self.rect.width, self.rect.height))
		self.image.set_alpha(0)

	def update(self):
		self.image.blit(self.surf, (0, 0))

	""" Causes the Image to actually appear """
	def makeVisible(self):
		self.image.set_alpha(255)
		self.image, junk = load_image_alpha(self.imageName)

""" A Sprite that represents a Team's Queue """
class Queue(pygame.sprite.Sprite):
	""" Draw a sprite representing the sorting queue """
	def __init__(self, numbers, coords, overlayColor = None):
		pygame.sprite.Sprite.__init__(self)
		self.backgroundColor = (235, 240, 255)
		self.numbers = numbers
		self.screen = pygame.display.get_surface()
		self.current = 0
		self.rect = pygame.Rect(0,0, 65*len(self.numbers), 65)
		x, y = coords
		self.rect.centerx = x
		self.image = pygame.Surface( (self.rect.width, self.rect.height) ) 
		self.image.fill( self.backgroundColor )
		
		self.area = self.screen.get_rect()
	
		self.numberBoxes = {}
		self._selected = None

		self.numColor = (9, 34, 106)
		self.numColorSelected = (255, 185, 34)
		self.borderColor = (157, 182, 255)
		self.overlayColor = overlayColor		

		if self.overlayColor == (255, 0, 0):
			self.arrow, self.arrowRect = load_image_alpha('arrowRed.png')
			self.queueBG, self.queueBGRect = load_image_alpha('queueBGBlue.png')
		else:
			self.arrow, self.arrowRect = load_image_alpha('arrowBlue.png')
			self.queueBG, self.queueBGRect = load_image_alpha('queueBGRed.png')
		self.surf = pygame.Surface( (self.rect.width, self.rect.height + self.arrowRect.height+2) )

		self.drawNumbers()
		
	def update(self):
		self.drawNumbers()

	def drawNumbers(self):
		font = pygame.font.SysFont('Verdana',  36)
		
		if self.current is None:
			 self.image.fill( self.backgroundColor )
			 return

		if len(self.numbers) == 0:
			 self.current = None
			 return None
		elif self.current >= len(self.numbers):
			 self.current = len(self.numbers) - 1
		elif self.current < 0:
			 self.current = 0
	   
	
		self.surf.blit(self.image, (0, 0))
		self.surf.fill( self.backgroundColor )			  
		x = 7


		for num in self.numbers:
			if num == self.numbers[self.current] and self._selected is not None:
				color = self.numColorSelected
				borderColor = self.numColorSelected
				borderWidth = 3
			elif num == self.numbers[self.current]:
				borderColor = self.numColorSelected
				color = self.numColor
				borderWidth = 3
			else:
				color = self.numColor
				borderColor = self.borderColor
				borderWidth = 1
			text = font.render( str(num), 4, color)
			textpos = text.get_rect()	 
			boundingBox = pygame.Rect(textpos)
			# make all the boxes the same width		   
			boundingBox.width = boundingBox.height
			boundingBox = boundingBox.move( (x, 7) )
			textpos = textpos.move( (x, 10) )
			boundingBox = boundingBox.inflate( 10, 10 )
			textpos = textpos.inflate(10, 10)
			#pygame.draw.rect(self.surf, (233, 252, 255), boundingBox)
			clipRect = pygame.Rect( (0, 0), (boundingBox.width, boundingBox.height))
			blitPos = self.surf.blit(self.queueBG, boundingBox, clipRect)
			pygame.draw.rect(self.surf, borderColor, boundingBox, borderWidth)
			self.numberBoxes[num] = boundingBox 
			"""	
			if not self.overlayColor == None:
				temp = pygame.Surface( (boundingBox.width, boundingBox.height) )
				temp.set_alpha(OVERLAY_ALPHA)	 
				pygame.draw.rect(temp, self.overlayColor, boundingBox)
				self.surf.set_alpha(254)
				self.surf.blit( temp, boundingBox)
				self.surf.set_alpha(254)
			"""

			if( boundingBox.width != textpos.width):
				textpos = textpos.move( (boundingBox.width + 12 - textpos.width)/2, 0 )		   
			#textpos = textpos.move( 10 , 0 )
			self.surf.blit( text, textpos )

			x += boundingBox.width + 8 
		
		# Now draw the arrow pointing to the next number to be inserted
		arrowPos = ( (boundingBox.width-self.arrowRect.width)/2, boundingBox.height + 4)
		self.surf.blit(self.arrow, arrowPos )	

		self.image = self.surf
	

	def swapNumbers(self, index1, index2):
		temp = self.numbers[index2]
		self.numbers[index2] = self.numbers[index1]
		self.numbers[index1] = temp
		
	def clicked(self, top_left):
		top, left = top_left
		for num in self.numberBoxes:
			numBox = self.numberBoxes[num]
			if numBox.collidepoint((top, left)):
				if self._selected == None:
					self._selected = num
				else:
					self.swapNumbers( self._selected, num)
					self._selected = None
				break

	def move(self, current):
		self.current = current

	def moveLeft(self):
		if self.current is None:
			return

		if self.current >= 1 :
			self.current -= 1
			
			if self._selected is not None :
				#self.swapLeft()
				self._selected = self.current
				
	def moveRight(self):
		if self.current is None:
			return

		if self.current < len(self.numbers)-1 :
			self.current  += 1
			
			if self._selected is not None :
				self._selected = self.current
			
	def select(self):
		self._selected = self.current
		
	def deselect(self):
		self._selected = None

	 
class SortNode:
	def __init__(self,value = None,root = None):
		pygame.init()
		self.value = value
		self.location = root
		self._font = pygame.font.SysFont('Verdana',35)
		self.backgroundColor = (235,240,255)
		self.textColor = (9,34,106)
		self.insertbg, self.insertbgrect = load_image_alpha('queueBG.png')
		self.image = pygame.Surface( (50,50) )
		self.surface = pygame.Surface( (50,50) )
		self.image.fill( self.backgroundColor )
		
	def draw(self):

		self.surface.blit(self.image,(0,0))
		self.surface.fill(self.backgroundColor)	
		
		if self.value == None:
			toPrint = '!'
		else:
			toPrint = self.value
			

		value = self._font.render(str(toPrint),True,self.textColor)
		valueRect = value.get_rect()
		valueRect.centerx = 25
		valueRect.centery = 25
		insertbgrect = pygame.Rect( (0,0) , (50,50) )
		self.surface.blit(self.insertbg,insertbgrect)
		pygame.draw.rect( self.surface,self.textColor,(0,0,50,50),1)
		self.surface.blit(value,valueRect)
		return self.surface

class GUITree(pygame.sprite.Sprite):
	def __init__(self, inRoot, inSortNode, location, overlayColor = (0, 0, 255)):
		pygame.sprite.Sprite.__init__(self)
		self._font = pygame.font.SysFont('Verdana',20)
		self.selected = False
		self.current = inRoot
		self.sortNode = inSortNode
		self.sortNodeLocation = None
		self.root = inRoot
		self.image = pygame.Surface( (576,764) )
		self.rect = self.image.get_rect()
		self.rect.topleft = location 
		self.bgcolor = (235,240,255)
		self.toUpdate = True
		self.overlayColor = overlayColor
		if self.overlayColor == (255, 0, 0):
			self.overlayColor = 'redtreenodebg'
		else:
			self.overlayColor = 'bluetreenodebg'

	def update(self):
		if self.toUpdate:
			self.toUpdate = False
			self.image.fill( self.bgcolor )
			self.drawTree(self.image,self.root,(50,0), self.rect.width / 2 - 50, root = 1)	
		
	def drawTree(self,surface,node,oldLocation,horizontalDistance, root = 0):
		newLocation = (oldLocation[0] + horizontalDistance,oldLocation[1] + 100)

		if not root:
			pygame.draw.line(surface,(colors['edgetree']),oldLocation,newLocation, 3)
		
		if node == self.sortNode.location:
			insertRect = pygame.Rect( (newLocation[0] - 25, newLocation[1] - 80),(50,50) )
			insertSurf = self.sortNode.draw()
			surface.blit(insertSurf, insertRect)
			
	
		newHDistance = abs(horizontalDistance) / 2	
		if node.right:
			self.drawTree(surface,node.right,newLocation,newHDistance)
		if node.left:
			newHDistance *= -1 
			self.drawTree(surface,node.left,newLocation,newHDistance)
		
		if node == self.current:
			if self.selected == True:
				theGuiNode = GNode(text = node.value, bgcolor = self.overlayColor, textcolor = 'treenodetext')
			else:
				theGuiNode = GNode(text = node.value, bgcolor = self.overlayColor, textcolor = 'treenodetext')
			surface.blit(theGuiNode.image,(newLocation[0] - 25, newLocation[1] - 25))
			pygame.draw.circle(surface,(255,185,34),newLocation,25,4)
		else:
			theGuiNode = GNode(text = node.value,bgcolor=self.overlayColor, textcolor = 'treenodetext')
			surface.blit(theGuiNode.image,(newLocation[0] - 25, newLocation[1] - 25))

	def move(self, current):
		self.current = current
		self.toUpdate = True
	
	def select(self):
		self.selected = self.current
		self.toUpdate = True
		
	def deselect(self):
		self.selected = None
		self.toUpdate = True
