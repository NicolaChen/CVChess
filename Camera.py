# import the necessary package
import time
import cv2
# import imutils
import threading

class Camera:

	def __init__(self):
		self.cam = cv2.VideoCapture(0)
		self.frame = None
		self.lock = threading.Lock()

	def cali(self):
		print("Calibration begins. Exit by press key 'Esc'.")
		if not self.cam.isOpened():
			print("Cam Open Fail. Try Again!")
		while self.cam.isOpened():
			self.lock.acquire()
			frame = self.frame
			self.lock.release()
			cv2.putText(frame, str(cv2.Laplacian(frame, cv2.CV_64F).var()), (100,100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0))
			cv2.putText(frame, 'w: '+str(frame.shape[1])+', h: '+str(frame.shape[0])+"var: "+str(3E8/(frame.shape[1] * frame.shape[0])), (100,200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0))
			cv2.putText(frame, str(cv2.mean(frame)[0]+cv2.mean(frame)[1]+cv2.mean(frame)[2]), (100,300), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0))
			cv2.imshow("calibration", frame)
			if cv2.waitKey(100) == 27:
				cv2.destroyWindow("calibration")
				break
	'''
	def takePicture(self):
		# allow the camera to warmup
		# time.sleep(1)
		if not self.cam.isOpened():
			self.cam = cv2.VideoCapture(0)
		# grab an image from the camera
		#i=0
		while True:
			ret, frame = self.cam.read()
			#i+=1
			if cv2.Laplacian(frame, cv2.CV_64F).var() > 4E8/(frame.shape[1] * frame.shape[0]):
				break
		print('Got one frame.')

		# resized = imutils.resize(image, height = 400, width = 400)
		scale = 0.5
		SIZE = (int(scale * frame.shape[1]), int(scale * frame.shape[0]))
		frame = cv2.resize(frame, SIZE)

		self.cam.release()
		return ret, frame
	'''

	def run(self):
		'''
		Adjust for multithreading
		'''
		while True:
			self.lock.acquire()
			ret, frame = self.cam.read()
			scale = 0.5
			SIZE = (int(scale * frame.shape[1]), int(scale * frame.shape[0]))
			self.frame = cv2.resize(frame, SIZE)
			self.lock.release()
			time.sleep(0.1)

	def getFrame(self):
		'''
		Adjust for multithreading
		'''
		self.lock.acquire()
		frame = self.frame
		self.lock.release()
		return frame
