import tkinter as tk
from tkinter import *

LARGE_FONT = ("system", 20)
MED_FONT = ("system", 12)
SMALL_FONT = ("system", 8)


class Application(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        gui = tk.Frame(self)
        gui.pack(side='top', fill="both", expand=True)
        gui.grid_rowconfigure(0, weight=1)
        gui.grid_columnconfigure(0, weight=1)

        self.frames = {}
        # self.game = Game()
        self.move = StringVar()
        self.move.set("e2e4")
        self.winner = StringVar()
        self.winner.set("Engine Wins!")

        for F in (StartGamePage, TestPage, Test2Page):
            frame = F(gui, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.showFrame(StartGamePage)

    def showFrame(self, f):
        frame = self.frames[f]
        frame.tkraise()
        if hasattr(frame, 'run'):
            frame.run()

    def destroyFrame(self):
        pass  # TODO: Figure out how to kill the program


# TODO: Adjust every label and button pack
class StartGamePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        title_label = tk.Label(self, text="ArmChess with Computer Vision", fg="blue", font=LARGE_FONT)
        title_label.pack(padx=150, pady=30)
        self.controller = controller
        start_button = tk.Button(self, text="Start Chess Game", font=MED_FONT,
                                 command=lambda: [controller.showFrame(TestPage)])
        start_button.pack(pady=30)

    def run(self):
        self.controller.showFrame(TestPage)


class TestPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.error_label = tk.Label(self, text="Error! Invalid move!\nMay be caused by camera, retry in",
                                    font=LARGE_FONT)
        self.error_label.pack()

        self.countdown_label = tk.Label(self, text="5 s")
        self.countdown_label.pack()

        self.ctr = controller

    def run(self):

        self.after(1000, self.countdown, 5)

    def countdown(self, n):
        n -= 1
        clock = self.after(1000, self.countdown, n)

        if n != 0:
            self.countdown_label["text"] = str(n) + " s"

        else:
            self.after_cancel(clock)
            self.countdown_label["text"] = "0"
            self.after(1000, self.ctr.showFrame, Test2Page)  # 或者可以直接运行


class Test2Page(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        tk.Label(self, text="Done").pack()
        tk.Button(self, text="return", command=lambda: [controller.showFrame(TestPage)]).pack()


app = Application()
app.mainloop()
