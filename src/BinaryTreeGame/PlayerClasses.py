from random import *
import math
from threading import Timer

""" The super 'Player' class """
class Player:
	# Builds default player class
	def __init__(self, params):
		self.wiiID = params['player']
		self.team = params['team']
		self.selected = None
		self.current = None
	
	# Lets a player select something
	# That something is determined by the actual type of player
	# Also checks if there is something to select
	def select(self):
		if self. current is not None:
			self.selected = self.current
		else:
			self.deselect
	
	# Lets a player deselect
	def deselect(self):
		self.selected = None
	
	def getName(self):
		return "Player"
	
	def printCurrent(self):
		print self.current
		
	def moveCurrent(self):
		return
	
	# Default shove function
	# shove corresponds to wiimote flicks taken by players
	def shove(self, direction):
		return
	
	# Default getNext function """
	def getNext(self, value):
		return
		
	# Default rotate function
	# rotate corresponds to rolling the wiimote
	def rotate(self, roll):
		return

	def rotateB(self, roll):
		return

""" The 'Sorter' class """
class Sorter(Player):
	""" Initializes extra 'Sorter' variables                              """
	""" current: the index in the Team's oppQueue that the player 'is On' """
	def __init__(self, params):
		Player.__init__(self, params)
		self.current = 0
		self.oppTeam = params['oppTeam']
		
	def getName(self):
		return "Sorter"
		
	def printCurrent(self):
		if self.current is None :
			print self.current
		else:
			print self.oppTeam.queue[self.current]
   
	""" Used to make sure that current never points outside the queue """  
	def moveCurrent(self):
		if len(self.oppTeam.queue) == 0 :
			self.current = None
		
		if self.current >= len(self.oppTeam.queue):
			self.current = len(self.oppTeam.queue) - 1
	
	""" Allows sorter to either swap values in the queue   OR   """
	""" Allows sorter to move to an adjacent value in the queue """
	def shove(self, direction):
		if self.current is None :
			return
		
		x, y = direction
		# If moving too far left or right, exit """
		if self.current <= 0 and x < 0 :
			return
		if self.current >= len(self.oppTeam.queue) - 1 and x > 0 :
			return
		
		# if selected swap in the specified direction
		if self.selected is not None :
			self.oppTeam.swapQueue(self.current, x)
			self.current += x
			self.selected = self.current
		# otherwise move in the specified direction
		else:
			if not (self.current == 0 and x < 0) and not \
				(self.current == len(self.oppTeam.queue) -1 and x >0) \
				and not self.current is None :
				
				self.current += x

class Inserter(Player):
	""" Initializes extra 'Inserter' variables """
	""" current: the number being inserted	   """
	"""    initialized to a random start #	   """
	""" center: The node that the Inserter is  """
	"""    is inserting from                   """
	def __init__(self, params):
		Player.__init__(self, params)
		
		self.current = self.team.getRandomNumber()
		self.center = self.team.tree.root
		self.timer = None
		
	def getName(self):
		return "Inserter"
	
	""" Allows inserter to move their value down the tree by moving left or right """
	""" Most of this functionality is in the tree                                 """ 
	""" Also, starts a timer that stops the Inserter from playing when they try   """
	"""   to insert a number wrong                                                """
	def shove(self, direction):
		x, y = direction
		if self.current is None:
			return

		# If there is a timer active, don't do anything
		if self.hasTimer():		
			return
		
		# Checks if the direction sorts the value correctly w.r.t the tree
		# if it is it updates the tree's last variable accordingly
		self.center, insert = self.team.tree.stillSorted(self.current, self.center, x)
		
		if insert == 'Middle':
			pass
		# If the player inserted into the correct tree, let them
		elif insert == True:
			self.center = self.team.affectTree(self.team.tree.insert, \
								 [self.current, self.center, x])
		# Otherwise, give them a timeout during which they can't do anything
		elif insert == False:
			self.startTimer() 
	
	""" Sets the Inseretr's current to a new value                      """
	""" Specifically used to get the next number from it's team's queue """
	def getNext(self, value):
		self.current = value
		self.center = self.team.tree.root
	
	""" Function that starts a three second timer            """
	""" An Inserter can't do anything during these 3 seconds """	
	def startTimer(self):
		if self.hasTimer():
			self.timer.cancel()
		self.timer = Timer(3.0, self.endTimer) 
		self.timer.start()

	""" Lets the inserter play again """
	def endTimer(self):
		self.timer = None

	""" Returns whether an Inserter has an active timer """
	def hasTimer(self):
		if self.timer == None:
			return False
		else:
			return True

""" The Rotator class """				
class Rotator(Player):
	""" Initializes extra 'Rotator' variables                       """
	""" current: where the cursor starts is at the root of the tree """
	def __init__(self, params):
		Player.__init__(self, params)
		self.current = self.team.tree.root
		
	def getName(self):
		return "Rotator"
	
	""" Prints the correct version of a Rotator's current	 """
	"""  by specifying that the 'current' node and its value """ 
	def printCurrent(self):
		print "Node:", self.current.value
	
	""" Allows the rotator to move to a left or right child or to a parent node """
	def shove(self, direction):
		if self.selected:
			return
		
		x, y = direction
		
		if y > 0 and self.current.parent :
			self.current = self.current.parent
			
		elif x < 0 and self.current.left :
			self.current = self.current.left
		elif x > 0 and self.current.right :
			self.current = self.current.right

	""" Tries to rotate the tree by a root if the rotator has rotated far enough """
	"""   and if the tree is actualy unbalanced                                  """
	def rotate(self, roll):
		if self.team.tree.checkBalanced(self.team.tree.root, 0) is not 'Unbalanced':
			return

		if abs(roll) > 1:
			self.current = self.team.affectTree(self.team.tree.rotateRoot, [self.current, roll] )
