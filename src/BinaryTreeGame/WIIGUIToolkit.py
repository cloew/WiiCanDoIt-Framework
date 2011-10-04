"""This is the WII GUI Toolkit, a python module put together to aid in
drawing the GUIs for both the Network Game and the Binary Tree Game
(originally).  Other code authors are free to modify this as needed -
feel free to add classes and functions to it if it would be useful
to do so in development of future game GUIs."""

import sys, os, pygame
from threading import Timer
from pygame.locals import *


pygame.init()
videoInfo = pygame.display.Info()
FULL_SCREEN_SIZE = (1024, 768)



# Capitalized to match the format of the Globals.py file.

colors = {'CKEY' : (0, 0, 0), 'BLUE' : (0, 0, 255), 'RED' : (255, 0, 0),
          'GREEN' : (0, 255, 0), 'YELLOW' : (255, 255, 0),
          'ORANGE' : (255, 100, 20), 'PINK' : (255, 100, 200),
          'PURPLE' : (145, 0, 200), 'BLACK' : (1, 1, 1),
	  'TREENODEBG' : (9, 34, 106), 'REDTREENODEBG' : (173, 0, 0),
	  'BLUETREENODEBG' : (0, 0, 173), 'TREENODETEXT' : (255,220,145),
          'EDGETREE' : (143,100,7), 'WHITE' : (255, 255, 255),
          'GRAY' : (200, 200, 200), 'DKGRAY' : (100, 100, 100)}


def Gload_image(name):
    """A function that merges the full path of the image name given, and
    loads the image.  This one's safe to use on images with per-pixel
    alpha values, since it uses image.convert_alpha() to convert the
    image pixels into the type of pixels the display has."""
    
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except:
        image = pygame.Surface((800, 800))
        image.fill(colors['CKEY'])
        image.set_colorkey(colors['CKEY'])
    image = image.convert_alpha()
    # Preserving per-pixel-alphas for semi-transparent to transparent
    # overlay images...
    return image

def Gdraw_bkg(type, color, radius):
    """This function draws either the colored node or colored packet
    background.  It takes a type, a color and a radius for pygame's
    draw circle or draw rect functions.  It draws the shape to a
    temporary surface and then it returns that surface.
    The default position is the center of the new surface, which is
    also the radius.

    The new background surface is twice the radius by twice the radius,
    to fit the whole shape comfortably... so if you want an image
    that's 50x50px, you should make a radius of 25.

    If you want to draw a packet, 'radius' becomes half the width of the
    packet square.

    NOTE:  The program's color key for transparency is black, which is
    titled 'CKEY' in the dictionary above.  'BLACK' is one pixel off of
    the color key, so that things which are colored using 'BLACK' look
    black, but are not actually true black.  Don't use (0, 0, 0) as the
    color argument for anything unless you want it transparent..."""
    
    bg = pygame.Surface((radius*2, radius*2))
    bg.set_colorkey(colors['CKEY'])
    if type == 'node':
        pygame.draw.circle(bg, colors[color], ((radius, radius)), radius)
    elif type == 'packet':
        pygame.draw.rect(bg, colors[color], (0, 0, radius*2, radius*2))
    return bg

def Gaspect_scale(img,(bx,by)):
    """ Scales 'img' to fit into box bx/by.
     This method will retain the original image's aspect ratio.

     Modified from Frank Raiser's original aspect_scale.py code,
     available here: http://www.pygame.org/pcr/transform_scale/index.php
     """
    ix,iy = img.get_size()
    if ix > iy:
        scale_factor = bx/float(ix)
        sy = scale_factor * iy
        if sy > by:
            scale_factor = by/float(iy)
            sx = scale_factor * ix
            sx = sx
            sy = by
        else:
            sx = bx
    else:
        scale_factor = by/float(iy)
        sx = scale_factor * ix
        if sx > bx:
            scale_factor = bx/float(ix)
            sx = bx
            sy = scale_factor * iy
        else:
            sy = by

    return pygame.transform.scale(img, (int(sx),int(sy)))

def Gequalize_images(fg, bg, ctr):
    """ This function makes sure that all of the images have the same
    size.  If the images are too large, they will be re-sized to the 
    size of the background image.  Smaller center images will be left 
    alone (which will *hopefully* fix the gigantic 11 problem in the 
    binary tree game)."""

    if not fg.get_size() == bg.get_size():
        #print 'Foreground size is not equal to background size, resizing'
        fg = pygame.transform.scale(fg, (bg.get_size()))
    if not ctr.get_size() == bg.get_size():
        if ctr.get_height() > int(.75 * bg.get_height()) or ctr.get_width() > int(.75 * bg.get_width()):
            #print 'Center size is not equal to background size, resizing'
            ctr = Gaspect_scale(ctr, bg.get_size())
            nw = int(ctr.get_width()*.75)
            nh = int(ctr.get_height()*.75)
            ctr = pygame.transform.scale(ctr, (nw, nh))
    return fg, ctr

class GButton():
    """This class creates the map buttons for the Network Game."""
    def __init__(self, myTuple):
        """This function takes a tuple; (button name, function call).
        The name is used as the text for the button right now.  The
        function call is the function the level builder calls to build the
        map.
        """
        
        self.bgimage = pygame.Surface(200, 100)
        self.bgimage.fill(colors['GRAY'])
        self.font = pygame.font.Font(None, 36)
        self.text = self.font.render(myTuple[0], 1, colors['WHITE'])
        self.ovr = Gload_image('button_overlay.png')
        self.ovr, self.text = Gequalize_images(self.ovr, self.bgimage,
                                              self.text)
        self.ovrpos = self.bgimage.get_rect(centerx=self.bgimage.get_width()/2,
                                            centery=self.bgimage.get_height()/
                                            2)
        self.textpos = self.ovrpos
        self.image = pygame.Surface(self.bgimage.get_size())
        self.image.blit(self.bgimage, (0, 0))
        self.image.blit(self.text, self.textpos)
        self.image.blit(self.ovr, self.ovrpos)
        self.function = myTuple[1]
            
    
    

class GNode(pygame.sprite.Sprite):
    """This is the Node class.  It makes a composite image out of 
    3 different images by painting them on the screen in a
    specific order.  The center image can either be a packet image (for
    the network game) or text (for the binary tree game).  The final
    result is a sprite object that can be easier manipulated by the
    GUI of either the Routing Game or the Binary Tree Game."""

    def __init__(self, text=None, bgradius=25, bgcolor='BLUE',
                 textcolor='WHITE', node = None):
        pygame.sprite.Sprite.__init__(self)
        """To initialize, you must pass the init function a radius for the
        background image (two times which will be the size of the node),
        a node color (default is 'blue'), and perhaps text (binary tree game
        only).  If you have text, you may pass a text color, if the default
        'white' won't look good."""

        self.type = 'node'
        self.color = bgcolor
        self.node = node
        self.bg = Gdraw_bkg(self.type, bgcolor, bgradius)
        self.rect = self.bg.get_rect()
        # self.bg is the background image of the composite.  For the
        # network game, it is a circle of a specific color.  If no color
        # is given, it will default to blue.

        self.fg = Gload_image('node_overlay.png')
        
        # self.fg is the overlay image of the composite.
 
        # I feel like I should explain this if-elif-else loop.
        # If 'text' is None and ctrimg is None, this will create a blank
        # center image to make an empty-looking node.

        # If 'text' is None and ctrimg is not None, this will load the
        # image of filename specified by 'ctrimg' and use that as the
        # middle layer of the composite image.

        # If 'text' is not None and ctrimg is None, this will render
        # a text-holding Surface to use as the center image.

        # Otherwise, (for now, at least) the program will exit due to
        # too many inputs from the user.  Later on, if it's desired,
        # both text and center-image inputs are possible, but for now
        # you will only want an image with one game, or text with the
        # other... never both at the same time."""
        
        if text is None: 
                self.ctr = pygame.Surface((bgradius*2, bgradius*2))
                self.ctr.fill(colors['CKEY'])
                self.ctr.set_colorkey(colors['CKEY'])
                # self.ctr is a blank, transparent surface.
                
	else:
            if text == 11:
                font = pygame.font.Font(None, 48)
            else:
                font = pygame.font.Font(None, 72)
        # Font for text. Sized so large so that it won't have to
        # be up-sized... scaling images down, even without sampling,
        # looks better than scaling them up.
        # Note: for some reason, in the binary tree game 11 resizes
        # to be really, really big.  Hence the custom text size
        # so that it doesn't look so horribly gigantic.
                
	    self.ctr = font.render(str(text), 1, colors[textcolor])
            # Render the text held in 'text' to a Surface.

        self.fg, self.ctr = Gequalize_images(self.fg, self.bg, self.ctr)
        # Gotta make sure that we don't have an overlay or a center
        # image that's bigger than our node is...
        self.bgpos = self.bg.get_rect(centerx=bgradius, centery=bgradius)
        self.ctrpos = self.ctr.get_rect(centerx=bgradius,centery=bgradius)
        self.fgpos = self.fg.get_rect(centerx=bgradius, centery=bgradius)
        self.temp = pygame.Surface((bgradius*2, bgradius*2))
        self.update()
        # Positioning all the images to be in the center of the surface.      

    def update(self):
        """This method:
            * Blanks out the temporary surface.
            * Blits the images to the temporary surface in their proper
              order.
            * Re-sets the sprite's self.image to the data contained in
              the temporary surface.

        This way, we end up with a 3D container-looking object
        out of three composite images.
        """ 
        self.fg, self.ctr = Gequalize_images(self.fg, self.bg, self.ctr)
        
        self.temp.fill(colors['CKEY'])
        self.temp.set_colorkey(colors['CKEY'])
        self.temp.blit(self.bg, self.bgpos)
        self.temp.blit(self.ctr, self.ctrpos)
        self.temp.blit(self.fg, self.fgpos)
        self.image = self.temp

	if not self.node == None:
	    packets = []
            i = 0
	    for x in self.node.packetQueue:
                packets.append(self.node.packetQueue[i])
                i += 1

            color1, color2, color3 = None, None, None

            if len(packets) > 0:
                color1 = packets[0]
            if len(packets) > 1:
                color2 = packets[1]
            if len(packets) > 2:
                color3 = packets[2]

            self.queueUpdate(color1, color2, color3)

    def queueUpdate(self, color1=None, color2=None, color3=None):
        """This is the node queue update function.  It gets called
        whenever the queue gets updated, and re-draws the center image
        of the node to reflect queue changes."""

        totalx = self.image.get_width()
        totaly = self.image.get_height()
        bBoxWidth = int(.5 * totalx)
        bBoxHeight = int(.5 * totaly)
        sBoxWidth = int(.25 * totalx)
        sBoxHeight = int(.25 * totaly)
        self.ctr.fill(colors['CKEY'])
        self.ctr.set_colorkey(colors['CKEY'])

        if not color1 == None:
            bigBoxBkg = pygame.Surface((bBoxWidth, bBoxHeight))
            bigBoxBkg.fill(colors[color1])
            bigBoxOvr = Gload_image('packet_overlay.png')
            bigBoxCtr = pygame.Surface((bBoxWidth, bBoxHeight))
            bigBoxCtr.fill(colors['CKEY'])
            bigBoxCtr.set_colorkey(colors['CKEY'])

            bigBoxOvr, bigBoxCtr = Gequalize_images(bigBoxOvr, bigBoxBkg,
                                                         bigBoxCtr)
            bBoxMash = pygame.Surface((bBoxWidth, bBoxHeight))
            bBoxMash.fill(colors['CKEY'])
            bBoxMash.set_colorkey(colors['CKEY'])
            bBoxMash.blit(bigBoxBkg, (0, 0))
            bBoxMash.blit(bigBoxCtr, (0, 0))
            bBoxMash.blit(bigBoxOvr, (0, 0))
            self.ctr.blit(bBoxMash, (int((.65/5.0)*totalx),
                                     int((1.30/5.0)*totaly)))
        else:
            bigBoxBkg = pygame.Surface((bBoxWidth, bBoxHeight))
            bigBoxBkg.fill(colors['CKEY'])
            bigBoxBkg.set_colorkey(colors['CKEY'])
            self.ctr.blit(bigBoxBkg, (0, 0))

        if not color2 == None:
            stBoxBkg = pygame.Surface((sBoxWidth, sBoxHeight))
            stBoxBkg.fill(colors[color2])
            stBoxOvr = Gload_image('packet_overlay.png')
            stBoxCtr = pygame.Surface((sBoxWidth, sBoxHeight))
            stBoxCtr.fill(colors['CKEY'])
            stBoxCtr.set_colorkey(colors['CKEY'])
            stBoxOvr, stBoxCtr = Gequalize_images(stBoxOvr, stBoxBkg, stBoxCtr)
            stBoxMash = pygame.Surface((sBoxWidth, sBoxHeight))
            stBoxMash.fill(colors['CKEY'])
            stBoxMash.set_colorkey(colors['CKEY'])
            stBoxMash.blit(stBoxBkg, (0, 0))
            stBoxMash.blit(stBoxCtr, (0, 0))
            stBoxMash.blit(stBoxOvr, (0, 0))
            self.ctr.blit(stBoxMash, (int(((.85/5.0)*totalx)+bBoxWidth),
                                      int(((1.5/5.0)*totaly))))
        else:
            stBoxBkg = pygame.Surface((sBoxWidth, sBoxHeight))
            stBoxBkg.fill(colors['CKEY'])
            stBoxBkg.set_colorkey(colors['CKEY'])
            self.ctr.blit(stBoxBkg, (0, 0))

        if not color3 == None:
            sbBoxBkg = pygame.Surface((sBoxWidth, sBoxHeight))
            sbBoxBkg.fill(colors[color3])
            sbBoxOvr = Gload_image('packet_overlay.png')
            sbBoxCtr = pygame.Surface((sBoxWidth, sBoxHeight))
            sbBoxCtr.fill(colors['CKEY'])
            sbBoxCtr.set_colorkey(colors['CKEY'])
            sbBoxOvr, sbBoxCtr = Gequalize_images(sbBoxOvr, sbBoxBkg, sbBoxCtr)
            sbBoxMash = pygame.Surface((sBoxWidth, sBoxHeight))
            sbBoxMash.fill(colors['CKEY'])
            sbBoxMash.set_colorkey(colors['CKEY'])
            sbBoxMash.blit(sbBoxBkg, (0, 0))
            sbBoxMash.blit(sbBoxCtr, (0, 0))
            sbBoxMash.blit(sbBoxOvr, (0, 0))
            self.ctr.blit(sbBoxMash, (int(((.85/5.0)*totalx)+bBoxWidth),
                                      int(((1.5/5.0)*totaly)+sBoxHeight)))

        else:
            sbBoxBkg = pygame.Surface((sBoxWidth, sBoxHeight))
            sbBoxBkg.fill(colors['CKEY'])
            sbBoxBkg.set_colorkey(colors['CKEY'])
            self.ctr.blit(sbBoxBkg, (0, 0))

class GPacket(pygame.sprite.Sprite):
    """A sprite class that will be used to represent network game packets
    on screen."""
    def __init__(self, color='RED', radius=25, text=None,
                 textcolor='white', callback = None):
        """This initialization function takes a color and packet size
        and draws the packet."""
        
        pygame.sprite.Sprite.__init__(self)
	self.type = 'packet'
        self.bg = Gdraw_bkg(self.type, color, radius/2)
        self.color = color
        self.fg = Gload_image('packet_overlay.png')
        self.rect = self.bg.get_rect()
        
        self.ctr = pygame.Surface((radius*2, radius*2))
        self.ctr.fill(colors['CKEY'])
        self.ctr.set_colorkey(colors['CKEY'])
        # self.ctr is a blank, transparent surface.
                
        self.fg, self.ctr = Gequalize_images(self.fg, self.bg, self.ctr)
        self.temp = pygame.Surface((radius*2, radius*2))
        self.update()
        self.MOVE_TICKS = 100.0
        self.callback = callback

    def _move(self):
        """This function moves the packet a percentage of the way to its
        destination.  Then starts a timer to move again, if the packet
        hasn't reached its destination."""

        if self.moves < self.MOVE_TICKS:
            self.setMoveTimer()
        elif self.callback:
           self.callback(self)

        self.moves += 1
        self.exactx += self.deltaX
        self.exacty += self.deltaY

        self.rect.centerx = self.startX + int(self.exactx)
        self.rect.centery = self.startY + int(self.exacty)

    def startSending(self, weight, oldpos, newpos):
        """ Begins a packet's movement to a destination """
        self.moves = 0
        
        self.startX, self.startY = oldpos
        self.exactx, self.exacty = 0.0, 0.0

        self.deltaX = (newpos[0] - oldpos[0])/self.MOVE_TICKS
        self.deltaY = (newpos[1] - oldpos[1])/self.MOVE_TICKS
        
        self.moveSpeed = (weight/10.0)/self.MOVE_TICKS
        
        self.setMoveTimer()

    def setMoveTimer(self):
        """ Sets the timer to move the Packet """
        timer = Timer(self.moveSpeed, self._move)
        timer.start()

    def update(self):
        """This method:
            * Blanks out the temporary surface.
            * Blits the images to the temporary surface in their proper
              order.
            * Re-sets the sprite's self.image to the data contained in
              the temporary surface.

        This way, we end up with a 3D-looking packet image composite from
        two separate images.
        
        NOTE: update's functionality may change once movement is
        incorporated into this class.  Watch for it!"""
        
        self.temp.fill(colors['CKEY'])
        self.temp.set_colorkey(colors['CKEY'])
        self.temp.blit(self.bg, (0, 0))
        self.temp.blit(self.ctr, (0, 0))
        self.temp.blit(self.fg, (0, 0))
        self.image = self.temp     

        
class GEdges(pygame.sprite.Sprite):
    
    def __init__(self, startpos, endpos, weight, thickness=5):
        """This initializes the GUI Edges class."""
        pygame.sprite.Sprite.__init__(self)
        self.weight = GWeights(startpos, endpos, weight)

        self.image = self.drawEdge(startpos, endpos, thickness)
        self.image.set_colorkey(colors['CKEY'])
        self.rect = self.image.get_rect()
        
    def drawEdge(self, startpos, endpos, thickness):
        """This function draws the edge onto the screen.  You must give it a
        starting position, ending position, and line thickness.  Make
        diagonals a little wider than horizontals or verticals; this will
        make them all look about the same width."""

        self.temp = pygame.Surface(FULL_SCREEN_SIZE)
        self.temp.fill(colors['CKEY'])
        self.temp.set_colorkey(colors['CKEY'])

        if not startpos[0] == endpos[0]:
            if not startpos[1] == endpos[1]:
                thickness = int(thickness * 1.5)
            # This makes the lines all *look* the same width - diagonals
            # don't look the same width as horizontals or verticals.
            # This is because it takes more pixels across on a diagonal
            # to draw diagonally.  Each diagonal line is a series of
            # stacked smaller lines offset by one pixel, with alpha
            # values per pixel for antialiased lines.
            
                               
        pygame.draw.line(self.temp, colors['BLACK'], startpos, endpos,
                         thickness)
        return self.temp


class GWeights(pygame.sprite.Sprite):
    """This class creates a sprite for the weights, and displays them on
    the screen.  Controlling a sprite's position is easier than
    controlling a raw image's position when it comes to Pygame."""
    
    def __init__(self, startpos, endpos, weight):
        """This function initializes the weight.  It takes its edge's
        starting and ending positions so that it can calculate where it
        should be positioned, in theory.  On some maps, however, weights
        may be colliding with other things if they are in the center
        of the line."""
        
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font(None, 24)
        self.image = self.font.render(str(weight), 1, colors['BLACK'])
        self.rect = self.image.get_rect()
        edgeWidth = endpos[0] + startpos[0] 
        edgeLength = endpos[1] + startpos[1]        
        midx = abs(edgeWidth)/2.0
        midy = abs(edgeLength)/2.0
        if not startpos[0] == endpos[0] and not startpos[1] == endpos[1]:
            offx = ((self.image.get_width() / 2) +
                    int(.10 * self.image.get_width()))
            offy = -1*((self.image.get_height() / 2) +
                       int(.10 * self.image.get_height()))
        elif not startpos[0] == endpos[0]:
            offx = -1*((self.image.get_width() / 2))
            offy = (int(self.image.get_height() * .10))
        else:
            offx = int(self.image.get_width() * .10)
            offy = -1*(self.image.get_height() / 2)
        self.rect.topleft = (midx + offx, midy + offy)
