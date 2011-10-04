from collections import deque
import time

from GameClass import *
from RouterNodeClass import *
from MapClass import *
from Levels import *

theGame = Game()

def Test_All():
    successes = 0
    testCount = 15
    successes += Node_Test()
    successes += Map_Test()
    successes += Player_Test()
    if successes == testCount :
        print "All Tests passed!!!"
    else:
        print successes,"out of", testCount

    raw_input()
def Node_Test():
    global theGame

    print "Testing node's ability to send, receive , and increment the score"
    successes = 0
    
    theGame.setMap(Map(2, 3, 10))
    theGame.addPlayer()
    theGame.addPlayer()
    
    node1 = RouterNode("GREEN", (.3, .3))
    node2 = RouterNode("YELLOW", (.5, .3))

    node1.add("YELLOW")
    node1.add("RED")
    
    packet1 = node1.sendPacket()
    packet2 = node1.sendPacket()

    node2.receivePacket(packet1, 8)
    node2.receivePacket(packet2, 10)

    print "Sending was a..."
    if node1.packetQueue == deque([]) :
        print "SUCCESS!!!"
        successes += 1
    else:
        print "FAILURE!!!"
        
    print "Receiving was a..."
    if node2.packetQueue.popleft() == "RED" :
        print "SUCCESS!!!"
        successes += 1
    else:
        print "FAILURE!!!"
        
    print "Scoring was a..."
    if theGame.score == 18 :
        print "SUCCESS!!!"
        successes += 1
    else:
        print "FAILURE!!! score was", theGame.score
    
    node2.add("BLUE")
    node2.add("PURPLE")
    node2.add("PINK")
    node2.add("ORANGE")
    
    node1.receivePacket(node2.sendPacket(), 8)
    node1.receivePacket(node2.sendPacket(), 8)
    node1.receivePacket(node2.sendPacket(), 8)
    node1.receivePacket(node2.sendPacket(), 8)
    
    
    print "Adding too many Packets..."
    if len(node1.packetQueue) == 3 :
        print "SUCCESS!!!"
        successes += 1
    else:
        print "FAILURE!!!"
        
    print "Adding penalty for lost Packets..."
    if theGame.score == 60 :
        print "SUCCESS!!!"
        successes += 1
    else:
        print "FAILURE!!! Score was", theGame.score
    
    raw_input()
    return successes
        
def Map_Test():
    global theGame

    print "Testing Map functions"
    successes = 0
    
    theGame.setMap(Map(2, 2, 10))
    map = theGame.mapOn
    
    node1 = RouterNode("GREEN", (.3, .3))
    node2 = RouterNode("YELLOW", (.5, .3))
    
    map.addNode(node1)
    map.addNode(node2)
    
    map.makeNeighbors(node1, node2, 8)
    
    node1.add("YELLOW")
    node1.add("RED")
    
    print "Testing if changes to nodes affect the map's list..."
    if map.nodeList[0].packetQueue.popleft() == "YELLOW" :
        print "SUCCESS!!!"
        successes += 1
    else:
        print "FAILURE!!!"
    
    dest, weight, inUse = map.checkNeighbors(node1, 1, 0)
    
    print "CheckNeighbors returns the correct destination and weight..."
    if dest == node2 and weight == 8 :
        print "SUCCESS!!!"
        successes += 1
    else:
        print "FAILURE!!!"
        
    dest.receivePacket(node1.sendPacket(), weight)
    
    print "Sending was a..."
    if node1.packetQueue == deque([]) :
        print "SUCCESS!!!"
        successes += 1
    else:
        print "FAILURE!!!"
        
    print "Receiving was a..."
    if node2.packetQueue.popleft() == "RED" :
        print "SUCCESS!!!"
        successes += 1
    else:
        print "FAILURE!!!"
    
    print "Scoring was a..."
    if theGame.score == 8 :
        print "SUCCESS!!!"
        successes += 1
    else:
        print "FAILURE!!! Score was", theGame.score
    
    raw_input()
    return successes

def Player_Test():
    global theGame

    print "Testing Player functionality"
    
    theGame.clearPlayers()
    
    theGame.addPlayer()
    theGame.addPlayer()
    
    successes = 0
    theGame.setMap(Map(3, 1, 10))
    map = theGame.mapOn
    
    node1 = RouterNode("RED", (.3, .3))
    node2 = RouterNode("YELLOW", (.4, .3))
    node3 = RouterNode("BLUE", (.5, .3))
    
    map.addNode(node1)
    map.addNode(node2)
    map.addNode(node3)
    
    map.makeNeighbors(node1, node2, 8)
    map.makeNeighbors(node2, node3, 16)
    
    node1.add("BLUE")
    
    theGame.getInput(2, 1, 0)
    
    print "Non-playing player can't send..."
    if len(node1.packetQueue) == 1 :
        print "SUCCESS!!!"
        successes += 1
    else:
        print "FAILURE!!!"
        
    theGame.getInput(0, 1, 1)
    
    print "Can't send in wrong direction..."
    if len(node1.packetQueue) == 1 :
        print "SUCCESS!!!"
        successes += 1
    else:
        print "FAILURE!!!"
    
    theGame.getInput(0, 1, 0)
    time.sleep(1)
    print "Legitimate sending..."
    if len(node2.packetQueue) == 1 and len(node1.packetQueue) == 0 :
        print "SUCCESS!!!"
        successes += 1
    else:
        print "FAILURE!!!"
        
    print "Scoring still working..."
    if theGame.score == 8 :
        print "SUCCESS!!!"
        successes += 1
    else:
        print "FAILURE!!!"
    
    map.packetsAdded = 1
    theGame.getInput(1, 1, 0)
    time.sleep(1.8)
    print "Game ends when all packets are received."
    if map.playing == 0 :
        print "SUCCESS!!!"
        successes += 1
    else:
        print "FAILURE!!!"
        

    raw_input()
    return successes

def Test_Game(somePlayers):
    global theGame

    print "Playing a Test Game"
    
    """ Init game variables """
    theGame.setMap(Big_Test_Level())
    map = theGame.mapOn
    theGame.clearPlayers()
    
    for x in range(somePlayers) :
        
        theGame.addPlayer()
    
    i = 0

    theGame.startGame(somePlayers)

    while(map.playing) :
        """ Getting input from user """
        if i < len(theGame.getPlayerList()) :
            print "Playing as", theGame.getPlayer(i).color, "Player"
        elif len(theGame.getPlayerList()) is not 0:
            print "Viewing", map.getNode(i).color, "Computer"
        stuff = raw_input()
        
        """ Movement input """
        if stuff == "a" :
            theGame.getInput(i, -1, 0)
        elif stuff == "s" :
            theGame.getInput(i, 0, -1)
        elif stuff == "d" :
            theGame.getInput(i, 1, 0)
        elif stuff == "w" :
            theGame.getInput(i, 0, 1)
        elif stuff == "aw" or stuff == "wa" :
            theGame.getInput(i, -1, 1)
        elif stuff == "dw" or stuff == "wd" :
            theGame.getInput(i, 1, 1)
        elif stuff == "as" or stuff == "sa" :
            theGame.getInput(i, -1, -1)
        elif stuff == "ds" or stuff == "sd" :
            theGame.getInput(i, 1, -1)
            
            """ Change Player """    
        elif stuff == "[" :
            if i != 0 :
                i -= 1
            else:
                print "Can't move that way"
        elif stuff == "]" :
            if i + 1 != len(theGame.getPlayerList()) :
                i += 1
            else:
                print "Can't move that way"
                
            """ Other Game Commands """
            
            """ Print commands"""
        elif stuff == "print node" :
            map.getNode(i).display()
        elif stuff == "print all" :
            map.printRouters()
        elif stuff == "print neighbors" :
            map.printNeighbors(i)
        
            """ Print the Score """
        elif stuff == "score" :
            print map.score
            """ Exit """
        elif stuff == "z" :
            map.playing = False
    
    theGame.endGame()
    print "Thanks for playing!!! You're score was", map.score
    print " You successfully routed", map.successfulPackets, "out of", map.maxPackets, "Packets"
    raw_input()
 
