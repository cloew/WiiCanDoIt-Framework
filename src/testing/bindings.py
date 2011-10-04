try:
	#sample bindings file
	from GameEventParser import GameEventCore
except:
	import sys, os
	sys.path.append( os.path.abspath(os.path.dirname("../"+os.path.dirname(__file__))))
	from GameEventParser import GameEventCore

class SampleGameEvents(GameEventCore.GameEventCore) :

	bind_funca 		= ['ButtonAPress', 'ButtonARelease'] 

#	bind_funcb		= [('ButtonAPress', 'ButtonBPress'), 'FlickY', ('ButtonARelease', 'ButtonBRelease')]

	bind_doStuff  	= ['ButtonBPress', 'Flick', 'ButtonBRelease'] 

	bind_rollA		= ['Button1Press', 'Roll', 'Button1Release']

print 'This is the bindings file'
