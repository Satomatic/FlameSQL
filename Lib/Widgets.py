import tkinter.ttk as ttk
from tkinter import *

def menubutton(frame=None, text=None, Font=None, command=None):
	buttonL = Label(frame, text=text, font=Font)
	
	def highlight(e):
		buttonL.config(bg="#cce8ff")
	
	def unhighlight(e):
		buttonL.config(bg="#ffffff")
	
	buttonL.bind("<Button-1>", command)
	#buttonL.bind("<Enter>", highlight)
	#buttonL.bind("<Leave>", unhighlight)
	
	return buttonL
