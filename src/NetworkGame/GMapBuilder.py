import os, sys, pygame
from pygame.locals import *
from WIIGUIToolkit import *
from BigGUI import FULL_SCREEN_SIZE


class GGameScreen():
    """ This is the class that controls the actual game screen.
    It takes care of displaying the Nodes, edges weights, and 
    Packets in transit """

    def __init__(self):
        """ Builds an empty screen with a blank surface 
        and no Node, Edge, Weight, or Packet sprites """

        self.surface = pygame.Surface(FULL_SCREEN_SIZE)
        self.surface.fill(colors['CKEY'])
        self.surface.set_colorkey(colors['CKEY'])

	self.nodeList = []
	self.edgeList = []
        self.weightList = []
        self.packetList = []

        self.allsprites = pygame.sprite.LayeredUpdates()
        self.running = 1

    def addNode(self, color, coords, node):
        """This function adds a node to the screen.  It receives a 
        string for the color, which it looks up in the WIIGUIToolkit 
        dictionary, and it also receives percentage-of-screen 
        coordinates, which it translates into pixels, accounting for
        the node's size (so it isn't drawn off the edge of the screen).
        """

        node = GNode(bgcolor=color, node = node)
        perx, pery = coords

        px = int(FULL_SCREEN_SIZE[0] * perx)
        py = int(FULL_SCREEN_SIZE[1] * pery)

        if (px + node.rect.width) > (FULL_SCREEN_SIZE[0]):
            px = px - ((px + node.rect.width) - FULL_SCREEN_SIZE[0])
        if (py + node.rect.height) > (FULL_SCREEN_SIZE[1]):
            py = py - ((py + node.rect.height) - FULL_SCREEN_SIZE[1])

        node.rect.topleft = (px, py)

	self.nodeList.append(node)
        self.allsprites = pygame.sprite.LayeredUpdates(self.edgeList,  self.weightList, self.packetList, self.nodeList)

    def findNode(self, inColor):
        """ Finds a GUI Node based on color """
        for node in self.nodeList:
            if node.color == inColor:
		return node

    def addEdge(self, startcoords, endcoords, weight):
        """This function creates an edge object and adds it to the map.
        As of right now, it takes starting and ending percentage 
        coordinates, a line thickness, and a weight.  The if-else
        block below simply turns the percentage coordinates into
        actual pixel values.  This will probably change."""
        
        perxi, peryi = startcoords
        perxf, peryf = endcoords

        widthPixi = int(FULL_SCREEN_SIZE[0] * perxi) + 25
        widthPixf = int(FULL_SCREEN_SIZE[0] * perxf) + 25
        heightPixi = int(FULL_SCREEN_SIZE[1] * peryi) + 25
        heightPixf = int(FULL_SCREEN_SIZE[1] * peryf) + 25
       
	edge = GEdges((widthPixi, heightPixi), (widthPixf, heightPixf), weight)

	self.edgeList.append(edge)
        self.weightList.append(edge.weight)
        self.allsprites = pygame.sprite.LayeredUpdates(self.edgeList, self.weightList, self.packetList, self.nodeList)

    """ Updates all sprites """
    def update(self):

        # Add all the Sprites in the appropriate order so Edges are on the bottom and Packets are on the top
        self.allsprites = pygame.sprite.LayeredUpdates(self.edgeList, self.weightList)
        self.allsprites.add(self.nodeList)
        self.allsprites.add(self.packetList)

        self.allsprites.update()

    """ Draws all sprites """
    def draw(self):
        # Blit the background
        self.surface.fill(colors['WHITE'])

        # Add all the Sprites in the appropriate order
        self.allsprites = pygame.sprite.LayeredUpdates(self.edgeList, self.weightList)
        self.allsprites.add(self.nodeList)
        self.allsprites.add(self.packetList)

        self.allsprites.draw(self.surface)


    """ This is a function to send a packet from a node """
    """ nodeColor: The color of the node that sent it for use in finding the GUI equivalent """
    """ packetColor: The color of the Packet being sent """
    """ Note: since the GUINode may actually already have that color, packetColor may change to the color of the next packet in the node's queue """
    """ This way it will be easy to tell a node what color it should display now """
    """ direction: is just the direction being sent so the packet knows where to go """
    def sendPacket(self, startColor, packetColor, endColor, weight):
        # Find the appropriate GUINode based on the given nodeColor and their coords on the screen
        startNode = self.findNode(startColor)
        endNode = self.findNode(endColor)

        startPos = (startNode.rect.centerx, startNode.rect.centery)
        endPos = (endNode.rect.centerx, endNode.rect.centery)
        
        # Build packet object based on the color of the Packet the GUINode already had
        packet = GPacket(color = packetColor, callback = self.removePacket)
        packet.rect.centerx, packet.rect.centery = startPos
        self.packetList.append(packet)
        
        # Tell the packet to animate to its destination and add the packet to the packetList
        packet.startSending(weight, startPos, endPos)

    def removePacket(self, packet):
        """ Destroys a Packet sprite so it no longer appears on the screen """
        self.packetList.remove(packet)
        del packet
