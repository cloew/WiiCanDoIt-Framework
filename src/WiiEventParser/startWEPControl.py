import sys, select
import WEPControl

if len(sys.argv) == 2:
	numPlayers = int(sys.argv[1])
else:
	numPlayers = None

WEPcontrol = WEPControl.WEPControl()

WEPcontrol.WiimoteGui(numPlayers)

input = [sys.stdin]

running = 1
while running:
	inputready, outputready, exceptready = select.select(input, [], [])
	for s in inputready:
		if s == sys.stdin:
			junk = sys.stdin.readline()
			running = 0
