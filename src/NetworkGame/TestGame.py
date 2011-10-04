from collections import deque
from RouterNodeClass import *
from Testing import *
from GameMain import *

while(True) :
    print """What would you like to do?
    1. Test all
    2. Test Nodes
    3. Test Maps
    4. Test Players
    5. Play a Test Game
    6. Watch Computers Play a Game
    7. Exit """
    stuff = raw_input()
    
    if stuff == "1" :
        Test_All()
    elif stuff == "2" :
        Node_Test()
    elif stuff == "3" :
        Map_Test()
    elif stuff == "4" :
        Player_Test()
    elif stuff == "5" :
        while True :
            print "How many players do you want?"
            stuff = raw_input()
            stuff = int(stuff)
            if stuff >= 0 and stuff <= 7 :
                Test_Game(stuff)
                break
            else:
                print "Sorry... didn't catch that? Please try again."               
    elif stuff == "6" :
        Test_Game(0)
    elif stuff == "7" :
        break
