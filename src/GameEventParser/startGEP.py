import sys
import GameEventCore

if not len(sys.argv) == 4:
	print "Killing the startGEP", sys.argv
	exit()

thisFile = sys.argv[0]
fileName = sys.argv[1]
className = sys.argv[2]
numPlayers = sys.argv[3]

print "Trying to execute", fileName
# Load in the bindings file
execfile(fileName)

command = 'bindings = ' + className + '(' + numPlayers + ')'

print "Trying to execute", command
exec(command)

bindings.start()
