import tkinter as tk
from tkinter import *
import threading
import time
import cv2

LARGE_FONT = ("system", 20)
MED_FONT = ("system", 12)
SMALL_FONT = ("system", 8)
lock = threading.Lock()

class Proc:
	def __init__(self):
		self.cam = cv2.VideoCapture(0)
		self.frame = None
		self.th = None

	def cap(self):
		while True:
			lock.acquire()
			ret, frame = self.cam.read()
			scale = 0.5
			SIZE = (int(scale * frame.shape[1]), int(scale * frame.shape[0]))
			self.frame = cv2.resize(frame, SIZE)
			#cv2.imshow('video', self.frame)
			#if cv2.waitKey(100) == 27:
				#break
			lock.release()
			time.sleep(0.5)

	def show(self):
		lock.acquire()
		cv2.imwrite('test.jpg', self.frame)
		print('cap once'+ str(self.frame.shape[1]))
		#cv2.waitKey(0)
		#cv2.destroyWindow('frame')
		lock.release()

class t:
	def __init__(self):
		self.proc = Proc()
	def get(self):
		th = threading.Thread(target = self.proc.cap, args = ())
		th.start()

class Application(tk.Tk):
	def __init__(self, *args, **kwargs):
		tk.Tk.__init__(self, *args, **kwargs)
		container = tk.Frame(self)
		container.pack(side = "top", fill = "both", expand = True)
		container.grid_rowconfigure(0, weight = 1)
		container.grid_columnconfigure(0, weight = 1)

		self.frames = {}
		self.t = t()
		
		for F in (StartGamePage, BoardPage):

			frame = F(container, self)
			self.frames[F] = frame
			frame.grid(row = 0, column = 0, sticky = "nsew")

		self.show_frame(StartGamePage)

	def show_frame(self, cont):
		'''
		Raises frame to top, displaying it as the current window
		'''

		frame = self.frames[cont]
		frame.tkraise()

class StartGamePage(tk.Frame):
	'''
	Prompts user to Start New Game
	'''

	def __init__(self,parent,controller):

		tk.Frame.__init__(self, parent)
		
		# set label
		label = tk.Label(self, text = "Threading frame capture test ", bg = "green", fg = "white", font = LARGE_FONT)
		label.pack(pady = 50, padx = 50)

		# set button that takes you to InitializeBoardPage and calls Game.setUp()
		startGameButton = tk.Button(self, text = "Start Test",font = MED_FONT,
						command = lambda: [controller.show_frame(BoardPage), controller.t.get()])
		startGameButton.pack()

class BoardPage(tk.Frame):
	def __init__(self, parent, controller):

		tk.Frame.__init__(self, parent)
		label = tk.Label(self, text = "Get One Frame From Video", font = LARGE_FONT)
		label.pack(pady = 10, padx = 10)
		frameCapButton = tk.Button(self, text = "Capture", font = MED_FONT, command = lambda : [controller.t.proc.show()]).pack()

app = Application()
app.mainloop()
