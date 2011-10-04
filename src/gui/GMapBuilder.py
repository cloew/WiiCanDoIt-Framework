import os, sys, pygame
from pygame.locals import *
from WIIGUIToolkit import *
from BigGUI import FULL_SCREEN_SIZE


class GGameScreen():
    def __init__(self):
        self.bkg = pygame.Surface(FULL_SCREEN_SIZE)
        self.bkg.fill(colors['CKEY'])
        self.bkg.set_colorkey(colors['CKEY'])

	self.nodeList = []
	self.edgeList = []
        self.packetList = []

        #self.nodeList = pygame.sprite.LayeredUpdates()
	#self.edgeSprites = pygame.sprite.LayeredUpdates()
	#self.packetSprites = pygame.sprite.LayeredUpdates()

        self.running = 1

        #return bkg

    def addNode(self, color, coords):
        """This function adds a node to the screen.  It receives a 
        string for the color, which it looks up in the WIIGUIToolkit 
        dictionary, and it also receives percentage-of-screen 
        coordinates, which it translates into pixels, accounting for
        the node's size (so it isn't drawn off the edge of the screen).
        """

        node = GNode(bgcolor=colors[color])
        perx, pery = coords

        px = int(FULL_SCREEN_SIZE[0] * perx)
        py = int(FULL_SCREEN_SIZE[1] * pery)

        if (px + node.width) > (FULL_SCREEN_SIZE[0]):
            px = px - ((px + node.width) - FULL_SCREEN_SIZE[0])
        if (py + node.height) > (FULL_SCREEN_SIZE[1]):
            py = py - ((py + node.height) - FULL_SCREEN_SIZE[1])

        node.rect.topleft = (px, py)

	self.nodeList.append(node)
	
        #bkg.blit(node.image, (x, y))
        #return bkg

    def findNode(inColor):
        for node in self.nodeList:
            if node.color == inColor;
		return node

    def addEdge(self, startcoords, endcoords, weight):
        """This function creates an edge object and adds it to the map.
        As of right now, it takes starting and ending percentage 
        coordinates, a line thickness, and a weight.  The if-else
        block below simply turns the percentage coordinates into
        actual pixel values.  This will probably change."""
	
	thickness = 8

        edge = GEdge(start, end, thickness, weight)
        perxi, peryi = startcoords
        perxf, peryf = endcoords

        widthPixi = int(FULL_SCREEN_SIZE[0] * perxi)
        widthPixf = int(FULL_SCREEN_SIZE[0] * perxf)
        heightPixi = int(FULL_SCREEN_SIZE[1] * peryi)
        heightPixf = int(FULL_SCREEN_SIZE[1] * peryf)

        px = abs(widthPixf - widthPixi)
        py = abs(heightPixf - heightPixi)

        if (px + edge.width) > FULL_SCREEN_SIZE[0]:
            px = px - ((px + edge.width) - FULL_SCREEN_SIZE[0])
        if (py + edge.height) > FULL_SCREEN_SIZE[1]:
            py = py - ((py + edge.height) - FULL_SCREEN_SIZE[1])

	self.edgeList.append(edge)
	
        #bkg.blit(edge.image, (px, py))

    """ tells this screen to perform all the actions necessary to have the screen display """
    """ The loop part will probably be moved to BigGUI, since this surface needs to be blitted to the window """
    def run(self):
        while self.running:
            """ Run the screen """

            """ update sprites """
            self.update()
            """ draw sprites and background """
            self.draw()

    """ Updates all sprites """
    def update(self):
        allsprites = pygame.sprite.LayeredUpdates(edgeList)

        """ If there are packets to display, add them to the sprite group """
        if self.packetList is not None:
            allsprites.add(packetList)

        allsprites.add(nodelist)

        allsprites.update()

    """ Draws all sprites """
    def draw(self):
        """ blit the background """
        allsprites = pygame.sprite.LayeredUpdates(edgeList)

        """ If there are packets to display, add them to the sprite group """
        if self.packetList is not None:
            allsprites.add(packetList)

        allsprites.add(nodelist)

        allsprites.draw(self.bkg)

    """ This is a function to send a packet from a node """
    """ nodeColor: The color of the node that sent it for use in finding the GUI equivalent """
    """ packetColor: The color of the Packet being sent """
    """ Note: since the GUINode may actually already have that color, packetColor may change to the color of the next packet in the node's queue """
    """ This way it will be easy to tell a node what color it should display now """
    """ direction: is just the direction being sent so the packet knows where to go """
    def sendPacket(self, nodeColor, packetColor, direction):
        """ Find the appropriate GUINode based on the given nodeColor """
        node = self.findNode(nodeColor)
        """ Build packet object based on the color of the Packet the GUINode already had """

        """ Tell the packet to animate to its destination and add the packet to the packetList """

        """ Tell the node to display the next packet in the queue, if any """

    def receivePacket(self, nodeColor, inPacket):
        """ Find the node """
        node = self.findNode(nodeColor)
        """ If the node doesn't have a packet, tell it to display the inPacket """
        #node.packet = inPacket and then the GUINode just knows to draw that color Packet
