from Tkinter import *
import GUINumberWiimotes
import GUIMessageDialog
import WiiEventParser
import WiimoteManager
import cwiid

class WEPControl:
	"""class that handles creating WiimoteManger, running the add wiimote gui, and
	creates a Wii event parser object if a game wants to use that directly. Our games do
	not make use of this parser"""

	def __init__(self):
		"""constructor that sets up parser and manager"""
		self.parser = WiiEventParser.WiiEventParser()
		self.manager = WiimoteManager.WiimoteManager()
		self._numMotes = None

	def __del__(self):
		"""Destructor, ends the parser if it is running"""
		print 'Destroying WEP Control'
		if	self.parser._isRunning:
			self.parser.end()

	def end(self):
		"""same call as destructor, shuts down the WEP process"""
		self.parser.end()

	def start(self):
		"""starts the Wii event parser included with the control"""
		self.parser.start()

	def addWiimotes(self, numMotes):
		"""command line way to add wiimotes to the wiimote manager.
		prompts in terminal to place wiimote in discoverable, creates the wiimote object"""
		self._numMotes = numMotes
		for x in range(numMotes):
			dummyString = 'Place wiimote number ' + str(x+1) + ' in discoverable mode and press ENTER:'
			dummy = raw_input(dummyString)
			newWiimote = cwiid.Wiimote()
			self.manager.addWiimote(newWiimote)

	def WiimoteGui(self, numMotes = None):
		"""gui version of addWiimotes, makes appropriate wiimote objects after gui prompts.
		if numMotes is none, a gui box pops up with a prompt for how many to sync"""
		w = 300
		h = 100
		if numMotes == None:
			#sets up the prompt to get the number of wiimotes to sync if no number passed to function
			root = Tk()
			root.title('Number of Wiimotes')
			app = GUINumberWiimotes.GUINumberWiimotes(root)
			screenWidth = root.winfo_screenwidth()
			screenHeight = root.winfo_screenheight()
			x = (screenWidth - w)/2
			y = (screenHeight - h)/2
			root.geometry('%dx%d+%d+%d' %(w, h, x, y))
			root.mainloop()
			root.withdraw()
			root.destroy()
			numMotes = app.numberWiimotes
		
		self._numMotes = numMotes
		for x in range(numMotes):#loops through making dialog boxes and adding wiimotes
			string = 'Place wiimote number ' + str(x + 1) + ' in discoverable mode and press OK.'
			newRoot = Tk()
			newRoot.title('Sync Wiimote')
			newApp = GUIMessageDialog.GUIMessageDialog(newRoot,string)
			screenWidth = newRoot.winfo_screenwidth()
			screenHeight = newRoot.winfo_screenheight()
			x = (screenWidth - w)/2
			y = (screenHeight - h)/2
			newRoot.geometry('%dx%d+%d+%d' %(w, h, x, y))
			newRoot.mainloop()
			try:	#creates wiimote object and adds the wiimote to the wiimote manager
				newMote = cwiid.Wiimote()
				self.manager.addWiimote(newMote)	
			except:
				print 'Error connecting Wiimote'
				break
			newRoot.withdraw()
			newRoot.destroy()
