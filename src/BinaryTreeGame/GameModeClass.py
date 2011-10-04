import sys
import os
import pygame
from pygame.locals import *

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from GameEventParser.GameEventCore import *
from WiiEventParser.WEPControl import *

from Bindings import *
from GUIMain import *
from MainScreenGUI import *

""" This is the default GameMode				   """
""" This class builds the Game's Main Screen	                   """
"""   and handles calls to every other game mode                   """
""" All other game modes should be child classes of this game mode """
"""  so they can all have access to the GUI and the ability to     """
"""  return to the MainScreen easily                               """
class GameMode:
    """ Builds a new Default Game Mode                       """
    """ Will set parameters based on a prevGameMode if given """
    def __init__(self):
        # Build the GUIMain     
        self.GUI = GUIMain(self)
        
    """ Starting this Game Mode builds the Main Screen """
    def startGame(self):
        self.GUI.runScreen(MainScreen(self))

    """ Function that returns any game mode to the main screen                   """
    """ Note: All gameModes should call their endGame functions before this call """
    """   and all gameEnd functions should make this call                        """
    def returnToMain(self):
        self = GameMode()
        self.startGame()
    
    """ Returns the screen that the GUI is currently running """
    def getScreen(self):
        return self.GUI.screen
