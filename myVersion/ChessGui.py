import time
import tkinter as tk
from tkinter import *

from Game import Game

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
        self.game = Game()
        self.move = StringVar()
        self.move.set("e2e4")
        self.winner = StringVar()
        self.winner.set("Engine Wins!")

        for F in (StartGamePage, InitializePage, SetBoardPage):
            frame = F(gui, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.showFrame(StartGamePage)

    def showFrame(self, f):
        frame = self.frames[f]
        frame.tkraise()

    def destroyFrame(self):
        pass  # TODO: Figure out how to kill the program


# TODO: Adjust every label and button pack
class StartGamePage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        title_label = tk.Label(self, text="ArmChess with Computer Vision", fg="blue", font=LARGE_FONT)
        title_label.pack(padx=150, pady=30)

        start_button = tk.Button(self, text="Start Chess Game", font=MED_FONT,
                                 command=lambda: [controller.showFrame(InitializePage), controller.game.setUp()])
        start_button.pack(pady=30)
        # TODO: Add arm gesture initialize code


class InitializePage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        cali_label = tk.Label(self, text="Please clear the BOARD for game set up", font=LARGE_FONT)
        cali_label.pack(padx=10, pady=10)

        cali_cam_button = tk.Button(self, text="View camera frames", font=MED_FONT,
                                    command=lambda: [controller.game.caliCam()])
        cali_cam_button.pack()

        init_board_button = tk.Button(self, text="Done", font=MED_FONT,
                                      command=lambda: [controller.showFrame(SetBoardPage),
                                                       controller.game.analyzeBoard()])
        init_board_button.pack(pady=20)


class SetBoardPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        set_board_label = tk.Label(self, text="Please set the BOARD", font=LARGE_FONT)
        set_board_label.pack()

        difficulty_button = tk.Button(self, text="Done", font=MED_FONT,
                                      command=lambda: [controller.showFrame(ChooseDifficultyPage),
                                                       controller.game.isBoardSet()])
        difficulty_button.pack()


class ChooseDifficultyPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        choose_difficulty_label = tk.Label(self, text="Please choose difficulty", font=LARGE_FONT)
        choose_difficulty_label.pack()

        tk.Button(self, text="Easy", font=MED_FONT,
                  command=lambda: [self.setEasy(controller), controller.showFrame(ChooseColorPage)]).pack()
        tk.Button(self, text="Intermediate", font=MED_FONT,
                  command=lambda: [self.setIntermediate(controller), controller.showFrame(ChooseColorPage)]).pack()
        tk.Button(self, text="Hard", font=MED_FONT,
                  command=lambda: [self.setHard(controller), controller.showFrame(ChooseColorPage)]).pack()
        tk.Button(self, text="Extreme", font=MED_FONT,
                  command=lambda: [self.setExtreme(controller), controller.showFrame(ChooseColorPage)]).pack()
        tk.Button(self, text="Master", font=MED_FONT,
                  command=lambda: [self.setMaster(controller), controller.showFrame(ChooseColorPage)]).pack()

    @staticmethod
    def setEasy(controller):
        controller.game.chessEngine.engine.configure({"Skill Level": 0})
        controller.game.chessEngine.time = 0.01

    @staticmethod
    def setIntermediate(controller):
        controller.game.chessEngine.engine.configure({"Skill Level": 5})
        controller.game.chessEngine.time = 0.1

    @staticmethod
    def setHard(controller):
        controller.game.chessEngine.engine.configure({"Skill Level": 10})
        controller.game.chessEngine.time = 1

    @staticmethod
    def setExtreme(controller):
        controller.game.chessEngine.engine.configure({"Skill Level": 15})
        controller.game.chessEngine.time = 3

    @staticmethod
    def setMaster(controller):
        controller.game.chessEngine.engine.configure({"Skill Level": 20})
        controller.game.chessEngine.time = 5


class ChooseColorPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        color_label = tk.Label(self, text="Please choose your color", font=LARGE_FONT)
        color_label.pack()

        white_button = tk.Button(self, text="White(Blue)", font=MED_FONT,
                                 command=lambda: [controller.showFrame(PlayerMovePage)])
        white_button.pack(pady=10)
        black_button = tk.Button(self, text="Black(Red)", font=MED_FONT,
                                 command=lambda: [controller.showFrame(EngineMovePage),
                                                  controller.move.set(controller.game.engineMove())])
        black_button.pack(pady=10)


class PlayerMovePage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        start_label = tk.Label(self, text="Chess game start! Waiting for your MOVE", font=LARGE_FONT)
        start_label.pack()

        resign_button = tk.Button(self, text="Resign", font=MED_FONT,
                                  command=lambda: [controller.showFrame(ConfirmPage)])
        resign_button.pack()
        self.waitPlayerMove(controller)

    def waitPlayerMove(self, controller):
        """
        Detect player's move and show in label, then check the game
        """
        # TODO: Combine detect&move, new function generates Game.playerMove
        controller.game.detectPlayerMove()

        show_move_label = tk.Label(self, text="Detect your move is:", font=LARGE_FONT)
        show_move_label.pack()

        player_move_label = tk.Label(self, textvariable=controller.game.playerMove, font=MED_FONT)
        player_move_label.pack()

        self.checkValid_P(controller)

    @staticmethod
    def checkValid_P(controller):
        """
        Check whether game is over/promotion/player error, if not, engine moves; contain Frame change
        """
        if controller.game.over:
            controller.winner.set(controller.game.winner)
            controller.showFrame(GameOverPage)
        elif controller.game.board.promo:
            controller.showFrame(ChoosePromotionPage)
        elif controller.game.PlayerMoveError:
            controller.game.current = controller.game.previous
            controller.showFrame(PlayerMoveErrorPage)
        else:
            controller.move.set(controller.game.engineMove())
            controller.showFrame(EngineMovePage)


class EngineMovePage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        engine_move_label = tk.Label(self, text="Engine Move:", font=LARGE_FONT)
        engine_move_label.pack()

        move_label = tk.Label(self, textvariable=controller.move, font=MED_FONT)
        move_label.pack()

        # TODO: Add Servo move control codes
        controller.game.updateCurrent()
        controller.game.checkEngineMove()  # Involving Game.boardMatchError

        self.checkValid_E(controller)

    @staticmethod
    def checkValid_E(controller):

        if controller.game.over:
            controller.winner.set(controller.game.winner)
            controller.show_frame(GameOverPage)
        elif controller.game.isCheck:
            controller.show_frame(InCheckPage)
        elif controller.game.boardMatchError:
            controller.game.current = controller.game.previous
            controller.show_frame(BoardMatchErrorPage)
        else:
            controller.show_frame(PlayerMovePage)


class ConfirmPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        confirm_label = tk.Label(self, text="Are you sure to RESIGN?", font=LARGE_FONT)
        confirm_label.pack(pady=10, padx=10)

        yes_button = tk.Button(self, text="Yes, resign", font=MED_FONT,
                               command=lambda: controller.showFrame(GameOverPage))
        yes_button.pack()
        no_button = tk.Button(self, text="No, continue", font=MED_FONT,
                              command=lambda: controller.showFrame(PlayerMovePage))
        no_button.pack()


class GameOverPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        over_label = tk.Label(self, text="Game over!", font=LARGE_FONT)
        over_label.pack(padx=10, pady=10)
        winner_label = tk.Label(self, textvariable=controller.winner, font=LARGE_FONT)
        winner_label.pack(padx=10, pady=10)

        quit_button = tk.Button(self, text="Quit", font=MED_FONT,
                                command=lambda: controller.destroyFrame())
        quit_button.pack(padx=30, pady=30)


class ChoosePromotionPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        choose_label = tk.Label(self, text="Choose your promotion", font=LARGE_FONT)
        choose_label.pack(pady=10, padx=10)

        queen_button = tk.Button(self, text="Queen(Q)",
                                 command=lambda: [self.setQueen(controller)])
        rook_button = tk.Button(self, text="Rook(R)",
                                command=lambda: [self.setRook(controller)])
        bishop_button = tk.Button(self, text="Bishop(B)",
                                  command=lambda: [self.setBishop(controller)])
        knight_button = tk.Button(self, text="Knight(N)",
                                  command=lambda: [self.setKnight(controller)])
        queen_button.pack()
        rook_button.pack()
        bishop_button.pack()
        knight_button.pack()

    @staticmethod
    def setQueen(controller):

        controller.game.board.promotion = 'q'
        controller.game.board.move = controller.game.board.move + 'q'
        controller.game.playerPromotion(controller.game.board.move)

        if controller.game.PlayerMoveError:
            controller.game.current = controller.game.previous
            controller.showFrame(PlayerMoveErrorPage)
        else:
            controller.move.set(controller.game.CPUMove())
            controller.showFrame(EngineMovePage)

    @staticmethod
    def setRook(controller):

        controller.game.board.promotion = 'r'
        controller.game.board.move = controller.game.board.move + 'r'
        controller.game.playerPromotion(controller.game.board.move)

        if controller.game.PlayerMoveError:
            controller.game.current = controller.game.previous
            controller.showFrame(PlayerMoveErrorPage)
        else:
            controller.move.set(controller.game.CPUMove())
            controller.showFrame(EngineMovePage)

    @staticmethod
    def setBishop(controller):

        controller.game.board.promotion = 'b'
        controller.game.board.move = controller.game.board.move + 'b'
        controller.game.playerPromotion(controller.game.board.move)

        if controller.game.PlayerMoveError:
            controller.game.current = controller.game.previous
            controller.showFrame(PlayerMoveErrorPage)
        else:
            controller.move.set(controller.game.CPUMove())
            controller.showFrame(EngineMovePage)

    @staticmethod
    def setKnight(controller):

        controller.game.board.promotion = 'n'
        controller.game.board.move = controller.game.board.move + 'n'
        controller.game.playerPromotion(controller.game.board.move)

        if controller.game.PlayerMoveError:
            controller.game.current = controller.game.previous
            controller.showFrame(PlayerMoveErrorPage)
        else:
            controller.move.set(controller.game.CPUMove())
            controller.showFrame(EngineMovePage)


class PlayerMoveErrorPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        error_label = tk.Label(self, text="Error! Invalid move!\nMay be caused by camera, retry in", font=LARGE_FONT)
        error_label.pack()

        self.countdown(controller)

    def countdown(self, controller):
        for cnt in reversed(range(5)):
            countdown_label = tk.Label(self, textvariable=cnt, font=MED_FONT)
            countdown_label.pack()
            time.sleep(1)

        controller.showFrame(PlayerMovePage)


class InCheckPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        check_label = tk.Label(self, text="You are in check!\nContinue in", font=LARGE_FONT)
        check_label.pack()

        self.countdown(controller)

    def countdown(self, controller):
        for cnt in reversed(range(5)):
            countdown_label = tk.Label(self, textvariable=cnt, font=MED_FONT)
            countdown_label.pack()
            time.sleep(1)

        controller.showFrame(PlayerMovePage)


class BoardMatchErrorPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        match_error_label = tk.Label(self, text="Board match error!\nMay be caused by camera, retry in",
                                     font=LARGE_FONT)
        match_error_label.pack()

        self.countdown(controller)

    def countdown(self, controller):
        for cnt in reversed(range(5)):
            countdown_label = tk.Label(self, textvariable=cnt, font=MED_FONT)
            countdown_label.pack()
            time.sleep(1)

        controller.showFrame(EngineMovePage)


# Start chess game
app = Application()
app.mainloop()
