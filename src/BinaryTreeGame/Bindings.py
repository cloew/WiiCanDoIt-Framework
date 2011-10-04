from GameEventParser.GameEventCore import *

class NoneBindings(GameEventCore):
	pass

""" The Main Set of Bindings """
class PlayerSelectionBindings(GameEventCore):
	
	bind_addPlayerA   = ['Button1Press']
	bind_addPlayerB   = ['Button2Press']
	bind_tryShove	  = ['Flick']
	bind_trySelect	  = ['ButtonAPress']
	bind_tryDeselect  = ['ButtonARelease']
	bind_tryRotate    = ['ButtonBPress', 'Roll', 'ButtonBRelease']

