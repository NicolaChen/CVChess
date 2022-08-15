import chess
import chess.engine


class ChessEng:
	"""
	This class interacts with the stockfish chess engine using the python-chess
	package. All interactions are done with the Universal Chess Interface protocol (UCI)
	Transcribes game to a txt file called ChessRecord.txt
	"""

	def __init__(self):
		"""
		Creates chessboard, local chess engine stockfish, and initiates UCI protocol
		"""
		self.engBoard = chess.Board()
		self.engine = chess.engine.SimpleEngine.popen_uci("./Stockfish-sf_15/src/stockfish")  # 采用官网的引擎引入方法
		self.time = 0.1
		print(self.engBoard)

	def updateMove(self, move):
        """
        Updates chess board with the move made. Also checks for illegal moves
        """
        uci_move = chess.Move.from_uci(move)
        if uci_move not in self.engBoard.legal_moves:
            # illegal move
            return 1
        else:
            # update board
            self.engBoard.push(uci_move)
            print(self.engBoard)
            return 0

	def feedToEngine(self):
        """
        Gets the best move from the stockfish engine. Writes move choice to ChessRecord.txt file
        """
        result = self.engine.play(self.engBoard, chess.engine.Limit(time=self.time))
        best_move = result.move
        self.engBoard.push(best_move)

        f = open("ChessRecord.txt", "a+")
        f.write(best_move.uci() + "\r\n")
        f.close()

        print(self.engBoard)
        return best_move
