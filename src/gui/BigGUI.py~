import os, sys, pygame, WIIGUIToolkit
from pygame.locals import *

from WIIGUIToolkit import *        
from MainScreenGUI import *

pygame.init()

videoInfo = pygame.display.Info()
FULL_SCREEN_SIZE = (videoInfo.current_w, videoInfo.current_h)
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
        pygame.display.set_caption('Network Game')
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill(colors['WHITE'])
        self.screen.set_colorkey(colors['CKEY'])
        self.displaying = None

        self.game = game

        # Construct the Main Menu Screen
        self.runScreen(MainScreen(self.game))

    def MenuScreen():
        """This function generates the main menu screen, and it will be
        called in the init function to display the main menu when the
        program is started."""

        self.displaying = MainScreen(self.game)

    def RolesScreen():
        """This function builds the roles screen.  This screen lets
        players choose what color node they are."""

        pass

    def MapSelectScreen():
        """This function calls the map selection screen.  Map selection
        will allow the players to choose a map, when that map is selected
        the levels class will be called to generate the level.  I'm not
        sure of the specifics of this one yet, aside from maybe a graphical
        representation of each map on each button, and clicking a button
        calls the function for that map..."""

        pass

    def PlayScreen():
        """This function calls the class to actually build the game map
        on the screen (I think?).  It will either be the most complicated
        function/class combination, or the least."""

        pass

    def GameOver():
        """ I haven't determined whether this will be its own screen, or
        if this will just display text saying the game is over, the time
        it took to route the packets and the score."""

        pass
    

    def update(self):
        """I don't know if I'll need a display update function, but
        why not have it just in case?  It can be removed later. ^.^"""
        
        pygame.display.flip()

    def run(self):
        global CLOCK_TICKER

        running = 1

        clock = pygame.time.Clock()

        while running:
            clock.tick(CLOCK_TICKER)

            self.getInput(pygame.event.get())

            if hasattr(self.displaying, "update"):
                self.displaying.update()
            else:
                self.allsprites.update()

            self.screen.blit(self.background, (0, 0))
            self.screen.blit(self.displaying.surface, (0, 0))
            
            if hasattr(self.displaying, "draw"):
                self.displaying.draw()
            else:
                print "in else statement..."
                self.allsprites.draw(self.screen)
            
            pygame.display.flip()

            if hasattr(self.displaying, "running"):
                running = self.displaying.running

    def runScreen(self, newScreen):
        self.displaying = newScreen
        
        if hasattr(newScreen, "allsprites"):
            self.allsprites = pygame.sprite.LayeredUpdates(newScreen.allsprites)

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
                self.checkClick()
        
            if hasattr(self.displaying, "getInput"):
                self.displaying.getInput([event])

    def checkClick(self):
        rect = pygame.Rect(pygame.mouse.get_pos(), (5, 5))

        for clickable in self.clickables:
            if rect.colliderect(clickable):
                clickable.clicked(rect.topleft)

def main():
    gui = GMap()

if __name__ == "__main__":
    main()
