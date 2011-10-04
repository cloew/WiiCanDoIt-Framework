import sys, os
import pygame

from pygame.locals import *

from GameboardClass import *

SCREEN_SIZE = (1152, 864)
BACKGROUND = (235,240,255)

""" Builds the screen for the Two Team Versus Mode game """
class TwoTeamVersusGameScreen:
    """ Builds both gameboards and adds their allsprites to the screens allsprites """
    def __init__(self, teams):
        global BACKGROUND
        
        # Set all variables to the defaults
        self.ending = 0
        self.surface = pygame.Surface(SCREEN_SIZE)
        
        self.surface.fill(BACKGROUND)
        
        self.gameboards = ([])
        self.gboardCoords = [(0,0), (576, 0)]
        
        # Build the Gameboards
        self.initGameboard(teams[0], (0, 0))
        self.initGameboard(teams[1], (576, 0))
        
        gboard1 = self.gameboards[0]
        gboard2 = self.gameboards[1]
        
        # Draw the Gameboards
        self.surface.blit(gboard1.surface, (0, 0))
        self.surface.blit(gboard2.surface, (576, 0))
        
        # Add the Gameboard's sprites to the screen's allsprites
        self.allsprites = pygame.sprite.LayeredUpdates(gboard1.allsprites, gboard2.allsprites)
        
    """ Function that builds the Gameboard objects """
    def initGameboard(self, team, coords):
        gameboard = Gameboard(team, coords)
        self.gameboards.append(gameboard)
        
    """ Updates a specific gameboard                   """
    """ This is called when either the Inserter        """
    """  has moved the insertSlot                      """
    """  or the rotator has moved the root of the Tree """
    def update(self, index):
        gboard = self.gameboards[index]
        gboard.update()
        gboard.guiTree.toUpdate = True

    """ Allows users to return to the main screen when the game is over """
    def getInput(self, events):
        for event in events:
            if event.type == MOUSEBUTTONDOWN and self.ending:
		return "exit"

    """ Tells a Gameboard to make their status button appear """
    def itsBalanced(self, index):
        self.gameboards[index].statusButton.show()
    
    """ Tells a Gameboard that it has won and should display accordingly """
    def drawWinner(self, index):
        self.gameboards[index].drawWinner()
	self.ending = 1
        
    """ Updates a Gameboard's Queue's currrent """
    def moveInQueue(self, index, current):
        self.gameboards[index].queue.move(current) 

    """ Updates a Gameboard's Queue's selected """   
    def selectQueue(self, index):
        self.gameboards[index].queue.select()
        
    """ Updates a Gameboard's Queue's selected """ 
    def deselectQueue(self, index):
        self.gameboards[index].queue.deselect()

    """ Updates a Gameboard's GUITree's current """
    def moveInTree(self, index, current):
        self.gameboards[index].guiTree.move(current)
        self.update(index)
        
    """ Updates a Gameboard's GUITree's current """
    def rotateTree(self, index, current):
        self.gameboards[index].guiTree.current = current
        self.update(index)
        
    """ Updates a Gameboard's GUITree's selected """
    def selectTree(self, index):
        self.gameboards[index].guiTree.select()
        
    """ Updates a Gameboard's GUITree's selected """
    def deselectTree(self, index):
        self.gameboards[index].guiTree.deselect()
