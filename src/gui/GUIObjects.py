import pygame, sys, os
from pygame.locals import *

try:
	from WIIGUIToolkit import *
except:
	location = os.path.dirname(os.path.abspath(__file__))
	sys.path.append(os.path.dirname(location) + '/gui')
	from WIIGUIToolkit import *
	
#from TreeClass import node

OVERLAY_ALPHA = 50 
BACKGROUND = (234, 240, 255)

def load_image(name, colorkey=None):
	fullname = os.path.join('data', name)
	try:
		image = pygame.image.load(fullname)
	except pygame.error, message:
		print "Cannot load image:", name
		raise SystemExit, message
	image = image.convert()
	if colorkey is not None:
		if colorkey is -1:
			colorkey = image.get_at((0,0))
		image.set_colorkey(colorkey, RLEACCEL)
	return image, image.get_rect()

def load_image_alpha(name):
	fullname = os.path.join('data', name)
	try:
		image = pygame.image.load(fullname)
	except pygame.error, message:
		print "Cannot load image:", name
		raise SystemExit, message
	image = image.convert_alpha()
	return image, image.get_rect()

class Hand(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image, self.rect = load_image_alpha("handPoint.png")
		self.clicking = 0
		self.x = x
		self.y = y
		
	def update(self):
		""" Move the hand image based on the mouse position """
		pos = (self.x, self.y)
		self.rect.midtop = pos
		if self.clicking:
			self.rect.move_ip(5, 10)
	
	" definitely need to edit to check if it hits any other buttons "
	def click(self, targets):
		""" The mouse buttojn is down """
		self.clicking = 1
				
		""" If nothing to interact with return """
		if not targets :
			return
		
		""" Check if clicked on anything """
		hitbox = self.rect.inflate(-5, -5)
		for target in targets :
			if hitbox.colliderect(target) :
				target.clicked(hitbox.topleft)
		
	def unclick(self):
		""" The mouse button is up """
		self.clicking = 0
		
class Button(pygame.sprite.Sprite):
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
		
		self.textStuff = self.addText()
		
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
		
		return (text, textpos)
		
	def update(self):
		text, textpos = self.textStuff
		
		self.drawBGRect(textpos)
		self.surf.blit(text, textpos)
		
		self.image = self.surf

	def drawBGRect(self, textpos):
		# First draw the background to fill the entire rectangle
		bgWidth = self.bgImageRect.width
		x = 0
		while x < self.rect.width:
			self.surf.blit(self.bgImage, (x, -10))
			x += bgWidth
		# Draw a bounding box
		boundingBox = textpos.inflate( 20, 20 )
		pygame.draw.rect(self.surf, self.borderColor, boundingBox, 1)	
		"""
		if not self.overlayColor == None:
			temp = pygame.Surface((boundingBox.width, boundingBox.height))
			pygame.draw.rect(temp, (255, 255, 255), boundingBox)
			pygame.draw.rect(temp, self.overlayColor, boundingBox)
			temp.set_alpha(OVERLAY_ALPHA)
			self.surf.blit(temp, (0,0))
			self.surf.set_alpha(254)
		"""
	def clicked(self, top_left):
		self.func()

class PlayerSelectButton(Button):
	def __init__(self, coords, inText, func = None, overlayColor = None):
		Button.__init__(self, coords, inText, func, overlayColor)	

	def highlight(self):
		self.bgImage, self.bgImageRect = load_image_alpha('buttonBGSelected.png')	

	# Don't do anything if it is clicked
	def clicked(self, top_left):
		self.highlight()
		
class StatusButton(Button):
	def __init__(self, coords, inText, func = None, overlayColor = None):
		global BACKGROUND

		Button.__init__(self, coords, inText, func, overlayColor)
		self.image = self.surf.fill(BACKGROUND)
		self.appear = 0
	
	def update(self):
		global BACKGROUND
		
		if self.appear:
			text, textpos = self.textStuff
		
			self.drawBGRect(textpos)
			self.surf.blit(text, textpos)
		else:
			self.surf.fill(BACKGROUND)
		self.image = self.surf
			
	def clicked(self):
		self.appear = 1
		self.setTimer()
		
	def setTimer(self):
		timer = Timer(2, self.stopAppearing)
		timer.start()
	
	def stopAppearing(self):
		self.appear = 0

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
		#self.rect.centery = y
		self.image = pygame.Surface( (self.rect.width, self.rect.height) ) 
		self.image.fill( self.backgroundColor )
		
		self.area = self.screen.get_rect()
	
		#self.rect.topleft = 10, 10
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

		print "In the init"
		for x in self.numbers:
			print x
		
		self.drawNumbers()
		
		print "After draw numbers"
		for x in self.numbers:
			print x

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
		print "Before"
		for x in self.numbers:
			print x
		
		temp = self.numbers[index2]
		self.numbers[index2] = self.numbers[index1]
		self.numbers[index1] = temp
		
		print "After"
		for x in self.numbers:
			print x
			
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
				print "swapping"
				#self.swapRight()
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
		'''if node.value == self.current:
			if self.selected == True:
				pygame.draw.circle(surface,(255,0,0),newLocation,25)
			else:
				pygame.draw.circle(surface,(0,0,255),newLocation,25)
			pygame.draw.circle(surface,(0,255,255),newLocation,25,5)
		else:
			pygame.draw.circle(surface,(0,0,255),newLocation,25)'''


		#value = self._font.render(str(node.value),True,(0,255,0))
		#valueRect = value.get_rect()
		#valueRect.centerx = newLocation[0]
		#valueRect.centery = newLocation[1]
		#surface.blit(value,valueRect)
		
	def moveLeft(self):
		#if self.selected is not None:
		if self.current.left:
			self.current = self.current.left
			self.toUpdate = True
			
	def moveRight(self):
		#if self.selected is not None:
		if self.current.right:
			self.current = self.current.right
			self.toUpdate = True
			
	def moveUp(self):
		#if self.selected is not None:
		if self.current.parent is not None:
			self.current = self.current.parent
			self.toUpdate = True
	
	def select(self):
		self.selected = self.current
		self.toUpdate = True
		
	def deselect(self):
		self.selected = None
		self.toUpdate = True
