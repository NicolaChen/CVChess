#import imutils
import cv2
import argparse
import chess
from ChessEng import ChessEng
from board_Recognition import board_Recognition
from Board import Board
from Camera import Camera
import threading
from datetime import datetime
import time

class Game:
	'''
	This class holds Game information interacting with the Board and Chess Engine
	'''

	def __init__(self):
		'''
		Initializes Game object	and creates several boolean values regarding game's status
		Sets game winner as place holder
		'''
		self.over = False
		self.CPUMoveError = False
		self.PlayerMoveError = False
		self.isCheck = False
		self.winner = "No one"
		self.camera = Camera()
		camthread = threading.Thread(target = self.camera.run)
		camthread.setDaemon(True)
		camthread.start()

	def setUp(self):
		'''
		Initializes objects with which the Game will interact
		'''	
		
		self.chessEngine = ChessEng()
		self.board = 0
		self.current = 0
		self.previous = 0
		self.CPULastMove = "0"

		# write record to txt file
		f = open("Game.txt", "a+")
		f.write("New Game, time: " + str(datetime.now()) + "\r\n")
		f.close()

	def caliCam(self):
		self.camera.cali()

	def analyzeBoard(self):
		'''
		Calls board_recognition to take image and initialize Board
		'''
		boardRec = board_Recognition(self.camera)
		self.board = boardRec.initialize_Board()
		self.board.assignState()

	def checkBoardIsSet(self):
		'''
		Takes inital picture of set board
		'''
		#camRet, self.current = self.camera.takePicture()
		time.sleep(5)
		while True:
			self.current = self.camera.getFrame()
			if cv2.Laplacian(self.current, cv2.CV_64F).var() > 3E8/(self.current.shape[1] * self.current.shape[0]):
				break

	def playerMove(self):
		'''
		Compares previous Board to current board to determine the movement made by the player
		'''
		self.previous = self.current
		#camRet, self.current = self.camera.takePicture()
		for i in range(30):
			self.current = self.camera.getFrame()
			if abs(cv2.mean(self.current)[0]+cv2.mean(self.current)[1]+cv2.mean(self.current)[2] - cv2.mean(self.previous)[0]-cv2.mean(self.previous)[1]-cv2.mean(self.previous)[2]) < 15 and cv2.Laplacian(self.current, cv2.CV_64F).var() > 3E8/(self.current.shape[1] * self.current.shape[0]):
				break
		move = self.board.determineChanges(self.previous,self.current)
		code = self.chessEngine.updateMove(move)
		if code == 1:
			# illegal move prompt GUI to open Player Move Error Page
			self.PlayerMoveError = True
		else:
			self.PlayerMoveError = False
			# write to Game.txt file
			f = open("Game.txt", "a+")
			f.write(chess.Move.from_uci(move).uci() + "\r\n")
			f.close()
		# check for Game Over
		if  self.chessEngine.engBoard.is_checkmate():
			self.winner = "You win!"
			self.over = True
			
	def playerPromotion(self, move):
		'''
		Compares previous Board to current board to determine the movement made by the player
		'''
		
		print(move)
		code = self.chessEngine.updateMove(move)
		if code == 1:
			# illegal move prompt GUI to open PlayerMoveError Page
			print("Error")
			self.PlayerMoveError = True
		else:
			self.PlayerMoveError = False
			
			# write to Game.txt file
			f = open("Game.txt", "a+")
			f.write(chess.Move.from_uci(move).uci() + "\r\n")
			f.close()

		# check Game Over
		if  self.chessEngine.engBoard.is_checkmate():
			self.winner = "You win!"
			self.over = True


	def CPUMove(self):
		'''
		Gets the CPU Move from the chess engine
		'''	

		# get move from chess engine
		self.CPULastMove = self.chessEngine.feedToAI()

		# if check GUI will open Check Window alerting user
		self.isCheck = self.chessEngine.engBoard.is_check()	

		# Check Game Over
		if self.chessEngine.engBoard.is_checkmate():
			self.winner = "CPU Wins!"
			self.over = True

		return self.CPULastMove

	def updateCurrent(self):
		'''
		Compares previous image of the board to the current picture to update.
		Ensures player has moved the CPU piece properly
		'''
		self.previous = self.current
		#self.camRet = False
		#while self.camRet == False:
		#	self.camRet, self.current = self.camera.takePicture()
		for i in range(30):
			self.current = self.camera.getFrame()
			if abs(cv2.mean(self.current)[0]+cv2.mean(self.current)[1]+cv2.mean(self.current)[2] - cv2.mean(self.previous)[0]-cv2.mean(self.previous)[1]-cv2.mean(self.previous)[2]) < 15 and cv2.Laplacian(self.current, cv2.CV_64F).var() > 3E8/(self.current.shape[1] * self.current.shape[0]):
				break

		# determine move
		move = self.board.determineChanges(self.previous, self.current)
		move = chess.Move.from_uci(move)

		# Ensure player has moved the CPU piece properly
		if move == self.CPULastMove:
			self.CPUMoveError = False
		else:
			# GUI will open CPUMoveError Page
			self.CPUMoveError = True

	def updatePrevious(self):
		'''
		Update previous frame in case identify errors caused by unexpected moves
		'''
		#self.camRet = False
		#while self.camRet == False:
		#	self.camRet, frame = self.camera.takePicture()
		while True:
			frame = self.camera.getFrame()
			if cv2.Laplacian(frame, cv2.CV_64F).var() > 3E8/(frame.shape[1] * frame.shape[0]):
				break

		print("Update Previous Frame Success.")
		self.current = frame
