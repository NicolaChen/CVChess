# import the necessary package
import time
import cv2
# import imutils

class Camera:

	def __init__(self):
		self.cam = cv2.VideoCapture(0)

	def takePicture(self):
		# allow the camera to warmup
		time.sleep(1)

		# initialize the camera and grab a reference to the raw camera capture
		if not self.cam.isOpened():
			print('!!!!!!Cam is not opened!!!!!!!')
			ret = False
			frame = None
			return frame

		# grab an image from the camera
		ret, frame = self.cam.read()
		print('Got one frame.\n')

		# resized = imutils.resize(image, height = 400, width = 400)


		return frame
