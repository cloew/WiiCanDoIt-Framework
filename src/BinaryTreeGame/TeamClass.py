from random import *

from TreeClass import Tree

MAX_NUMBER = 25

""" The Team class """
class Team:
    """ Builds the default Team                                       """
    """ teamName: Holds a string for the Team's name                  """
    """ playerList: Holds the Player objects associated with the Team """
    """ queue: Holds the Teams sequence of numbers that must be added """
    """   and sorted into the tree                                    """
    """ tree: Holds the Team's Tree object                            """
    def __init__(self, teamName, game):
        self.teamName = teamName
        self.game = game
        self.playerList = ([])
        self.queue = ([])
        self.tree = Tree()
        
        self.setUpGameboard()
    
    """ Adds a Player to the team """
    def addPlayer(self, player):
        self.playerList.append(player)
    
    """ Removes all Players from the team """
    def clearPlayers(self):
        self.playerList = ([])
        
    def getPlayerByRole(self, inRole):
        for player in self.playerList :
            if player.getName() == inRole :
                return player
        
        return None
        
    """ Builds the Team's queue with random numbers from 0-25                           """
    """ The getRandomNumber function ensures these numbers have not been used earlier   """
    def setUpGameboard(self):
        for x in range(5) :
            x = self.getRandomNumber()
            self.queue.append(x)
            
    """ Generates a random Number that a Team hasn't used before """
    """   (that's not in the queue or the root of the tree)      """  
    def getRandomNumber(self):
        picked = False
        while not picked :
            picked = True
            x = random()*MAX_NUMBER
            x = int(x)
            
            if x == self.tree.root.value :
                picked = False
                continue
            for val in self.queue :
                if x == val :
                    picked = False
                    break
            if picked:
                return x
    
    """ Allows sorter to swap numbers in the 'queue' """
    def swapQueue(self, current, direction):
        temp = self.queue[current]
        self.queue[current] = self.queue[current + direction]
        self.queue[current + direction] = temp
        
    """ Gets the next number out of the list """
    def getNextNumber(self):
        # Check if the Game is over
        if len(self.queue) == 0:
            self.game.gameOver(self)
            return
        
        # Get the value
        value = self.queue[0]
        self.queue.remove(value)
        
        # Move Player's currents to make sure they still point at something
        for team in self.game.teams :
            if team != self :
                break
        
        player = team.getPlayerByRole("Sorter")
        player.moveCurrent()
        
        # Return the value
        return value
  
    """ Called when players want to affect the tree                      """
    """ This allows the Team to check if the tree is balanced or not     """
    """   after the alteration                                           """
    """ If the tree is balanced, it pops the first number from its queue """
    """   and sends it to the Team's Inserter                            """
    """ If the tree is not balanced, it sends None to the Inserter       """
    def affectTree(self, action, params):
        result = action(params)
        
        balanced = self.tree.checkBalanced(self.tree.root, 0)
        
        if balanced is not "Unbalanced":
            theNum = self.getNextNumber()
            self.game.itsBalanced(self)
        else:
            theNum = None
            self.getPlayerByRole("Inserter").center = self.tree.root
        
        for x in self.playerList :
            x.getNext(theNum)
        
        return result
    
    """ Prints the Team's queue """ 
    def printQueue(self):
        print "Team", self.teamName
        print "Queue:",
        for x in self.queue:
            print x,
        print ""
        
    """ Prints the Team's tree """
    def printTree(self):
        self.tree.printTree(self.tree.root)
