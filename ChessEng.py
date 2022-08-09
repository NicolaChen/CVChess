import chess
import chess.engine
# import chess.uci
import numpy as np
# import stockfish
from Board import Board

class ChessEng:
	'''
	This class interacts with the stockfish chess engine using the python-chess
	package. All interactions are done with the Universal Chess Interface protocol (UCI)
	Transcribes game to a txt file called Game.txt
	'''

	def __init__(self):
		'''
		Creates chessboard, local chess engine stockfish, and initiates UCI protocol
		'''

		self.engBoard = chess.Board()
		self.engine = chess.engine.SimpleEngine.popen_uci("/home/orangepi/Downloads/stockfish_15_linux_x64/stockfish_15_src/src/stockfish")		#采用官网的引擎引入方法
		self.time = 0.1
		print(self.engBoard)

	def updateMove(self, move):
		'''
		Updates chess board with the move made. Also checks for illegal moves
		'''

		# convert move to UCI format for engine
		uciMove = chess.Move.from_uci(move)

		# check legality
		if uciMove not in self.engBoard.legal_moves:
			return 1
		else:
			# update board
			self.engBoard.push(uciMove)
			print(self.engBoard)
			return 0


	def feedToAI(self):
		'''
		Gets the bestmove from the stockfish engine. Writes move choice to Game.txt file
		'''

		# giving the CPU the current board position
		result = self.engine.play(self.engBoard, chess.engine.Limit(time=self.time))
		bestMove = result.move
		
		# update board
		self.engBoard.push(bestMove)
		
		# write move to txt file
		f = open("Game.txt", "a+")
		f.write(bestMove.uci()+ "\r\n")
		f.close()
		
		print(self.engBoard)
		return bestMove
