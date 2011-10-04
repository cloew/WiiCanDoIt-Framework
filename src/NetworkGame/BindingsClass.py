from GameEventParser.GameEventCore import *

""" This class holds the single wiimote binding for the Network Game      """
""" It connects a flick of the wiimote to the Game's filterInput function """
class Bindings(GameEventCore) :

    bind_filterInput     = ['Flick']
