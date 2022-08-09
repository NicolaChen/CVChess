# import the necessary package
import time
import cv2
# import imutils

class Camera:

	def __init__(self):
		self.cam = cv2.VideoCapture(0)

	def cali(self):
		print("Calibration begins. Exit by press key 'Esc'.")
		if not self.cam.isOpened():
			print("Cam Open Fail. Try Again!")
		while self.cam.isOpened():
			ret, frame = self.cam.read()
			scale = 0.5
			SIZE = (int(scale * frame.shape[1]), int(scale * frame.shape[0]))
			frame = cv2.resize(frame, SIZE)
			cv2.putText(frame, str(cv2.Laplacian(frame, cv2.CV_32F).var()), (100,100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0))
			cv2.imshow("calibration", frame)
			if cv2.waitKey(100) == 27 or cv2.Laplacian(frame, cv2.CV_64F).var() > 4E8/(frame.shape[1] * frame.shape[0]):
				cv2.destroyWindow("calibration")
				self.cam.release()
				break

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
