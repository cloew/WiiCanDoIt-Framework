from Tkinter import *
import GUIMessageDialog

class GUINumberWiimotes:
	"""class that prompts for number of wiimotes to sync"""
	def __init__(self,master,caption="Please enter the number of Wiimotes to sync"):
		"""sets up the gui dialog"""
		self.frame = Frame(master)
		self.frame.pack()
		self.caption = caption
	
		self.instruction = Label(self.frame,text = self.caption, wraplength=300)
		self.textEntry = Entry(self.frame)
		self.textEntry.focus_set()
		self.okButton = Button(self.frame, text = 'OK', fg = 'red', bg = 'black', command = self.callback)
		self.instruction.pack(side = TOP)
		self.textEntry.pack(side = LEFT)
		self.okButton.pack(side = RIGHT)

	def callback(self):
		"""callback function, closes the frame and sets the numberWiimotes value to what the user entered"""
		try:
			self.numberWiimotes = int(self.textEntry.get())
			self.frame.quit()
		except:
			print 'Letters are not integers!'

