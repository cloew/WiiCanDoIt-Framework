"""This is the WII GUI Toolkit, a python module put together to aid in
drawing the GUIs for both the Network Game and the Binary Tree Game
(originally).  Other code authors are free to modify this as needed -
feel free to add classes and functions to it if it would be useful
to do so in development of future game GUIs."""

import sys, os, pygame
from pygame.locals import *
pygame.init()
videoInfo = pygame.display.Info()
FULL_SCREEN_SIZE = (videoInfo.current_w, videoInfo.current_h)



# Capitalized to match the format of the Globals.py file.

colors = {'CKEY' : (0, 0, 0), 'BLUE' : (0, 0, 255), 'RED' : (255, 0, 0),
          'GREEN' : (255, 0, 0), 'YELLOW' : (255, 255, 0),
          'ORANGE' : (255, 100, 20), 'PINK' : (255, 100, 200),
          'PURPLE' : (145, 0, 200), 'BLACK' : (1, 1, 1),
          'TREENODEBG' : (9, 34, 106), 'TREENODETEXT' : (255,220,145),
          'SELECTEDTREENODEBG' : (28,154,178),
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
        #print 'File not found:', fullname, '.'
        #print 'Using a blank surface instead...'
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
    temporary variable and then it returns that variable.
    The default position is the center of the new surface, which is
    also the radius.

    The new background surface is twice the radius by twice the radius,
    to fit the whole shape comfortably... so if you want an image
    that's 50x50px, you should make a radius of 25.

    If you want to draw a packet, 'radius' becomes half the width of the
    packet square.

    NOTE:  The program's color key for transparency is black.
    DO NOT USE (0, 0, 0) FOR YOUR COLOR, UNLESS YOU DON'T WANT A
    VISIBLE BACKGROUND CIRCLE.  You can use any value other than that,
    though."""
    
    bg = pygame.Surface((radius*2, radius*2))
    bg.set_colorkey(colors['CKEY'])
    if type == 'node':
        pygame.draw.circle(bg, colors[color], ((radius, radius)), radius)
    elif type == 'packet':
        pygame.draw.rect(bg, colors[color], (0,0,radius,radius))
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

    def __init__(self, type='node', text=None, ctrimg=None, bgradius=25,
                 bgcolor='BLUE', textcolor='white', pos=(0, 0)):
        pygame.sprite.Sprite.__init__(self)
        """To initialize, you must pass the init function a type (in this
        case, 'node', to draw a node), either text, a center image, or
        neither (the default is None in both cases), a radius for the
        background image (two times which will be the size of the node),
        and a node color (default is 'blue').  If you have text, you may
        pass a text color, if the default 'white' won't look good."""
        
        self.color = bgcolor
        self.bg = Gdraw_bkg(type, bgcolor, bgradius)
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
            if ctrimg is None:
                self.has_packet = False
                #print 'Debug: Blank Node Drawn'
                # self.has_packet is true if the package image should exist.
                # Since it's false, no packet image should be drawn here."""
                
                self.ctr = pygame.Surface((bgradius*2, bgradius*2))
                self.ctr.fill(colors['CKEY'])
                self.ctr.set_colorkey(colors['CKEY'])
                # self.ctr is a blank, transparent surface.
                
            else:
                self.has_packet = True
                #print 'Debug: Packet Node Drawn'
                #print 'Packet is', os.path.join('data', ctrimg)
                # self.has packet is true, so the packet image should be drawn.
                
                self.ctr = Gload_image(ctrimg)
                # self.ctr is the image specified by ctrimg.
                
        elif text is not None:
            if ctrimg is None:
                #print 'Debug: Text Node Drawn'
                #print 'Text is', text
                self.has_packet = False
                # self.has_packet is false, so no packet image here.
            
                font = pygame.font.Font(None, 72)
                # Font for text. Sized so large so that it won't have to
                # be up-sized... scaling images down, even without sampling,
                # looks better than scaling them up.
                
                self.ctr = font.render(str(text), 1, colors[textcolor])
                # Render the text held in 'text' to a Surface.

            else:
                #print 'Error: too many inputs.'
                SystemExit

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
        
        self.temp.fill(colors['CKEY'])
        self.temp.set_colorkey(colors['CKEY'])
        self.temp.blit(self.bg, self.bgpos)
        self.temp.blit(self.ctr, self.ctrpos)
        self.temp.blit(self.fg, self.fgpos)
        self.image = self.temp

    def queueUpdate(self, color1=None, color2=None, color3=None):
        """This is a prototype for the node queue update function.  It
        gets called whenever the queue gets updated, and re-draws the
        center image of the node to reflect queue changes."""

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

            self.update()
            
            

    def sndrcvpacket(self, packet=None, rcv=False, snd=False):
        """This function is called whenever the node must send or
        receive a packet.  When you want the node to receive a packet,
        set rcv to true and pass it a packet sprite to pull the image 
        from.  When you want the node to send a packet, just set snd
        to true, and it will take care of the rest."""

        if rcv == True:
            if self.has_packet == True:
                self.ctr = packet.image
            elif self.has_packet == False:
                self.has_packet = True
                self.ctr = packet.image            
        if snd == True:
            self.ctr = pygame.Surface(self.bg.get_size())
            self.ctr.fill(colors['CKEY'])
            self.ctr.set_colorkey(colors['CKEY'])
    

class GPacket(pygame.sprite.Sprite):
    """A sprite class that will be used to represent network game packets
    on screen."""
    def __init__(self, type='packet', color='RED', radius=25, text=None, textcolor='white', bgradius=25, pos=(0, 0)):
        """This initialization function takes a color and packet size
        and draws the packet."""
        
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
        self.bg = Gdraw_bkg(type, color, radius)
        self.color = color
        self.fg = Gload_image('packet_overlay.png')
        self.rect = self.bg.get_rect()
        
        self.ctr = pygame.Surface((bgradius*2, bgradius*2))
        self.ctr.fill(colors['CKEY'])
        self.ctr.set_colorkey(colors['CKEY'])
        # self.ctr is a blank, transparent surface.
                
        self.fg, self.ctr = Gequalize_images(self.fg, self.bg, self.ctr)
        self.temp = pygame.Surface((radius*2, radius*2))
        self.bgpos = self.bg.get_rect(centerx=radius, centery=radius)
        self.fgpos = self.fg.get_rect(centerx=radius, centery=radius)
        self.ctrpos = self.ctr.get_rect(centerx=radius, centery=radius)
        self.update()

    def _move(self, newpos, weight=60):
        """This function handles packet movement.  It takes the top
        corner of the node it's moving to, and the weight of the edge
        it's moving across."""
        #threading.timer 
        #nx, ny = newpos
        #cx, cy = self.pos

        #mx = nx - cx
        #my = ny - cy

        
        

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
        self.temp.blit(self.bg, self.bgpos)
        self.temp.blit(self.ctr, self.ctrpos)
        self.temp.blit(self.fg, self.fgpos)
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
        diagonals about 2-3 px wider than horizontals or verticals; this will
        make them all look about the same width."""

        self.temp = pygame.Surface(FULL_SCREEN_SIZE)
        self.temp.fill(colors['CKEY'])
        self.temp.set_colorkey(colors['CKEY'])

        #if not startpos[0] == endpos[0]:
        #    if not startpos[1] == endpos[1]:
        #        thickness = int(thickness * 2.75)
            # This makes the lines all *look* the same width - diagonals
            # don't look the same width as horizontals or verticals.
            # This is because it takes almost 3 times the pixels across
            # on a diagonal to draw diagonally.  Each diagonal line is a
            # series of stacked smaller lines offset by one pixel, with
            # alpha values per pixel for antialiased lines.
            
                               
        pygame.draw.line(self.temp, colors['BLACK'], startpos, endpos,
                         thickness)
        return self.temp


class GWeights(pygame.sprite.Sprite):
    def __init__(self, startpos, endpos, weight):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font(None, 24)
        self.image = self.font.render(str(weight), 1, colors['BLACK'])
        self.rect = self.image.get_rect()
        edgeWidth = endpos[0] + startpos[0] 
        edgeLength = endpos[1] + startpos[1]        
        midx = abs(edgeWidth)/2.0
        midy = abs(edgeLength)/2.0
        if not startpos[0] == endpos[0] and not startpos[1] == endpos[1]:
            offx = ((self.image.get_width() / 2) + int(.10 * self.image.get_width()))
            offy = -1*((self.image.get_height() / 2) + int(.10 * self.image.get_height()))
        elif not startpos[0] == endpos[0]:
            offx = -1*((self.image.get_width() / 2))
            offy = (int(self.image.get_height() * .10))
        else:
            offx = int(self.image.get_width() * .10)
            offy = -1*(self.image.get_height() / 2)
        self.rect.topleft = (midx + offx, midy + offy)
        
