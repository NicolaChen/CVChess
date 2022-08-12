import threading
import time
from datetime import datetime

import cv2

from BoardRecognition import BoardRecognition
from Camera import Camera
from ChessEng import ChessEng


class Game:

    def __init__(self):
        self.camera = Camera()
        self.board = None
        self.current = None
        self.engine_last_move = None
        self.chess_engine = ChessEng()
        self.is_check = False
        self.winner = ""
        self.over = False

        self.player_move_error = False
        self.board_match_error = False
        self.previous = None
        self.move_flag = False

    def setUp(self):
        """
        Prepare camera thread and start it; Write new record beginning to txt file
        """
        cam_thread = threading.Thread(target=self.camera.run)
        cam_thread.setDaemon(True)
        cam_thread.start()

        f = open("ChessRecord.txt", "a+")
        f.write("New chess game at: " + str(datetime.now()) + "\n")
        f.close()

    def caliCam(self):
        self.camera.cali()

    def analyzeBoard(self):
        board_recognize = BoardRecognition(self.camera)
        self.board = board_recognize.initializeBoard()
        self.board.assignState()

    def isBoardSet(self):
        time.sleep(2)  # Give camera some time to focus, can be dismissed
        while True:
            self.current = self.camera.getFrame()
            if cv2.Laplacian(self.current, cv2.CV_64F).var() > 3E8 / (self.current.shape[1] * self.current.shape[0]):
                break

    def engineMove(self):
        """
        Feed current board to engine; Return engine's new move
        """
        self.engine_last_move = self.chess_engine.feedToEngine()
        self.is_check = self.chess_engine.engBoard.is_check()
        if self.chess_engine.engBoard.is_checkmate():
            self.winner = "Engine Wins!"
            self.over = True
        return self.engine_last_move
