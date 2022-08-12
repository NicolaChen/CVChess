import threading
import time
from datetime import datetime

import cv2

from BoardRecognition import BoardRecognition
from Camera import Camera
from ChessEng import ChessEng


class Game:

    def __init__(self):
        self.over = False
        self.playerMoveError = False
        self.boardMatchError = False
        self.isCheck = False
        self.winner = ""
        self.camera = Camera()
        self.chessEngine = ChessEng()
        self.board = None
        self.current = None
        self.previous = None
        self.engineLastMove = ""
        self.moveFlag = False

    def setUp(self):
        cam_thread = threading.Thread(target=self.camera.run)
        cam_thread.setDaemon(True)
        cam_thread.start()

        f = open("ChessRecord.txt", "a+")
        f.write("New chess game at: " + str(datetime.now()) + "\r\n")
        f.close()

    def caliCam(self):
        self.camera.cali()

    def analyzeBoard(self):
        board_recognize = BoardRecognition(self.camera)
        self.board = board_recognize.initializeBoard()
        self.board.assignState()

    def isBoardSet(self):
        time.sleep(2)  # give camera some time to focus, can be dismissed
        while True:
            self.current = self.camera.getFrame()
            if cv2.Laplacian(self.current, cv2.CV_64F).var() > 3E8 / (self.current.shape[1] * self.current.shape[0]):
                break

    def engineMove(self):
        """
        Do: feed board to engine
        RETURN: engine's new move
        """
        self.EngineLastMove = self.chessEngine.feedToEngine()
        self.isCheck = self.chessEngine.engBoard.is_check()
        if self.chessEngine.engBoard.is_checkmate():
            self.winner = "Engine Wins!"
            self.over = True
        return self.EngineLastMove
