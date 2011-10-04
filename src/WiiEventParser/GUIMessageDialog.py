from Tkinter import *

class GUIMessageDialog:
	"""GUI used for prompting to press ok when the device is in discoverable"""
	def __init__(self,master,message):
		"""initializes the window to prompt with the message passed in"""
		self.frame = Frame(master)
		self.frame.pack()
   
		self.instruction = Label(self.frame,text = message, wraplength=300)
		self.okButton = Button(self.frame, text = 'OK', fg = 'red', bg = 'black', command = self.frame.quit)
		self.okButton.pack(side = BOTTOM)
		self.instruction.pack(side = TOP)

