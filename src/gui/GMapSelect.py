import os, sys, pygame
from pygame.locals import *
from WIIGUIToolkit import *
from BigGUI import FULL_SCREEN_SIZE

bufferx = (FULL_SCREEN_SIZE[0] - int(FULL_SCREEN_SIZE[0] * .10))
buffery = (FULL_SCREEN_SIZE[1] - int(FULL_SCREEN_SIZE[1] * .10))
bufferposx = int(FULL_SCREEN_SIZE[0] * .05)
bufferposy = int(FULL_SCREEN_SIZE[1] * .05)


"""This class is responsible for drawing the map selection screen.
Each map has a button that for right now will display text, but
later on, perhaps it will display a dot-and-line representation
of the map's layout.  Clicking the button will return what map is
being played to the big GUI, both as text and as a function call to be
passed to the level builder once an instance of the map is created.
"""

class MapPicker():
    def __init__(self):
        """Right now, this function initializes what's on the map
        picker screen based on hard-coded values.  Later on it could be
        useful to figure out how to abstract away the hard coding and
        generalize it, so if people create new levels this will take
        perhaps a list of tuples and generates and places buttons from
        there.  Perhaps a Version 1 or 2 thing, since this is Version
        0?
        """
        mapbg = pygame.Surface(FULL_SCREEN_SIZE)
        mapbg.fill(colors['CKEY'])
        mapbg.set_colorkey(colors['CKEY'])

        pygame.font.Font(None,72)
        title = pygame.font.render("Wii Route Stuff", 1,
                                   colors['BLACK'])
        
        titleSize = title.get_size()
        adjbuffery = buffery - titleSize[1]
        adjbufferx = bufferx
        count = 0
        
        maps = [('smallTest', Levels.Test_Level()),
                ('bigTest', Levels.Big_Test_Level())]
        buttonList = []

        mapbg.blit(title, (((bufferx/2)-(titleSize[0]/2)), bufferypos))

        for stuff in maps:
            count = count + 1

        for x in range(count):
            index = count-1            
            buttonList.append(GButtonBuilder(maps[index]))
            
            if (bufferxpos + buttonList[index].get_width() > bufferx):
                # Will blitting this exceed the buffer size?
                # If so, "return" to the next line of images.
                # Will "returning" exceed the buffer's height?
                # If so, exit with an error.
                
                bufferxpos = int(FULL_SCREEN_SIZE[0] * 0.05)
                if (bufferypos + buttonList[index].get_height() >
                    buffery):
                    print 'Error: Too many maps to display properly.'
                    SystemExit

                bufferypos = bufferypos + buttonList[index].get_height()
                
            mapbg.blit(buttonList[index], (bufferxpos, bufferypos))
            bufferxpos = bufferxpos + buttonList[index].get_width()
