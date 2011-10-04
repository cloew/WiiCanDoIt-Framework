from GUIObjects import *

HALF_SIZE_SCREEN = (576, 864)
BACKGROUND = (235, 240, 255)

""" This class holds the GUI information for a Team                        """
""" Holds the Team's visual Queue, insertSlot, and Tree                    """
""" Also, contains the visual timer for when an Inserter makes a mistake,  """
"""  the phrase that tells a team they've balanced the tree, and the crown """
"""  that appears when a team has balanced all numbers in their queue      """

class Gameboard:
	""" Sets up the default gameboard and all the Sprites it needs """
	def __init__(self, team, coords):
		global HALF_SIZE_SCREEN, BACKGROUND

		self.surface = pygame.Surface(HALF_SIZE_SCREEN)
		self.surface.fill(BACKGROUND)
		
		self.team = team
		self.insertSlot = None
		self.color = None
		self.coords = coords
		
		# Builds the button that appears to tell the team that they've balanced the tree or won the game
		x, y = coords
		maxX, maxY = HALF_SIZE_SCREEN
		centeredCoords = (x + maxX/2, 3*maxY/4 + 100)
		
		self.statusButton = StatusButton(centeredCoords, "TREE IS BALANCED!!!", None, self.color)

		# Builds the crown container so that it can displayed if necessary
		centeredCoords = (x + maxX/2, maxY/4 - 100)
		self.crownContainer = ImageContainer("crown.png", centeredCoords)

		# Selects the Team's color based on the Team's name
		if self.team.teamName == 'Red':
			self.color = (255, 0, 0)
		elif self.team.teamName == 'Blue':
			self.color = (0, 0, 255)
		
		# Build the displayed queue based on the internal queue 
		centeredCoords = (x + maxX/2, 50)
		self.queue = Queue(team.queue, centeredCoords, self.color)
		
		# Build the insertion slot based on the inserter's current
		player = team.getPlayerByRole("Inserter")
		
		if player :
			self.insertSlot = SortNode(player.current, player.center)
		else:
			print "For some reason the game is getting called with a team without an Inserter. This shouldn't be happening"


		# Build the GUITimer that counts down when an Inserter tries to Insert wrong
		self.insertTimer = GUITimer(player, (coords[0] + 272, coords[1] + 300), self.color)

		# Build the displayed tree based on the team's tree
		self.guiTree = GUITree(team.tree.root, self.insertSlot, (coords[0], coords[1] + 100), self.color)
		
		# Add all the sprites so they can be updated and drawn correctly
		self.allsprites = pygame.sprite.LayeredUpdates(self.queue, self.guiTree, self.statusButton, self.insertTimer, self.crownContainer)
	
	""" Resets the insertSlot to the Inserter's values, and """
	"""  resets the GUITree to be rooted at the actual root """
	def update(self):
		# Reset the insertSlot
		player = self.team.getPlayerByRole("Inserter")
		
		if player :
			self.insertSlot = SortNode(player.current, player.center)

		# Reset the Tree
		self.guiTree.root = self.team.tree.root			   
		self.guiTree.sortNode = self.insertSlot
	
	""" Displays the appropriate effects when this Team wins """
	def drawWinner(self):
		# Set the Status Button to declare the Victors
		self.statusButton.text = "You are the Wii Tree Kings!!!"
		self.statusButton.addText()
		self.statusButton.appear = 1
		self.statusButton.fade = 0

		# Crown the victors by making the crownContainer visible
		self.crownContainer.makeVisible()
