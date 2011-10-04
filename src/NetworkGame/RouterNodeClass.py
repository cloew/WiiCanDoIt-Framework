from collections import deque
from threading import Timer

""" This is the RouterNode class                       """
""" The code-level represention of a node on the map   """
""" Contains a queue to hold the 'Packets'             """
""" Contains a string that holds the color of the node """
""" Contains methods to add 'Packets' to the queue     """
""" Contains methods to send and receive 'Packets'     """

""" Notes:                                                                  """
""" In comments, 'node' refers to an object of the Router Node class        """
""" In comments, 'Packet' refers to a color string ("YELLOW", "GREEN", etc) """
"""   not an actual instantiation of a Packet class                         """
class RouterNode:  
    """ Builds an empty RouterNode given its color """
    def __init__(self, startColor, coord): 
        self.packetQueue = deque([])
        self.color = startColor
        self.coord = coord
    
    """ Adds a 'Packet' to the end of a node's packetQueue """    
    def add(self, color):
        self.packetQueue.append(color)
    
    """ Sends the first 'Packet' in a node's queue to """
    """ the end of an adjacent node                   """
    """ Returns the first Packet in the packetQueue   """
    def sendPacket(self):
        if self.packetQueue == deque([]) :
            return
        
        return self.packetQueue.popleft()
    
    """ Receives a packet and adds it to its queue """
    def receivePacket(self, inColor):
        self.add(inColor)
        
    """ Prints the node's queue """
    def display(self):
        print self.color, "Node has:"
        if self.packetQueue :
            for x in self.packetQueue :
                print "  ", x, "Packet"
        else:
            print "   Nothing"
