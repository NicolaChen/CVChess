import threading
import time

lock = threading.Lock()

class CAP:
	def __init__(self):
		self.counter = 0

	def run(self):
		print("Starting")
		while True:
			lock.acquire()
			self.counter += 1
			lock.release()
			print("Now cnt: " + str(self.counter))
			time.sleep(1)

	def printCnt(self):
		lock.acquire()
		print("Get Count: " + str(self.counter))
		lock.release()
cap = CAP()
th1 = threading.Thread(target = cap.run, args = ())
th2 = threading.Thread(target = cap.printCnt, args = ())
th1.start()
for i in range(10):
	cap.printCnt()

	time.sleep(3)
