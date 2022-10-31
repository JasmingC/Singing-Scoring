from tkinter import *
from tkinter import ttk
import tkinter as tkinter
import time as t

import sys

gui=Tk()
gui.title('progress')
gui.geometry('600x150')

def StartProgress():
    # start progress
    progress_var.start(sys.argv[2])
    
    
def StopProgress():
    # stop progress
    progress_var.stop()
# create an object of progress bar

l = tkinter.Label(gui, text=sys.argv[1], font=('Times New Roman', 16,'bold'), fg='#112052', width=30, height=2, anchor='s')
l.pack()
progress_var=ttk.Progressbar(gui,orient=HORIZONTAL, style="red.Horizontal.TProgressbar",length=400,mode='determinate')
progress_var.pack(pady=30)


StartProgress()
gui.mainloop()