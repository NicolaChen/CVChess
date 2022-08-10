import cv2
import numpy as np
import math

class Square:

	def __init__(self, image, c1, c2, c3, c4, position, scale, state=''):

		# Corners
		self.c1 = c1
		self.c2 = c2
		self.c3 = c3
		self.c4 = c4

		# Position
		self.position = position

		# npArray of corners
		self.contour = np.array([c1,c2,c4,c3],dtype=np.int32)

		# Center of square
		M = cv2.moments(self.contour)
		cx, cy = int(M['m10'] / M['m00']), int(M['m01'] / M['m00'])

		# ROI for image differencing
		self.roi = (cx, cy)
		self.radius = int(scale * 0.3)

		self.emptyColor = self.roiColor(image)
		self.emptyGray = self.roiGray(image)
		self.state = state

	def draw(self, image, color,thickness=2):

		# Formattign npArray of corners for drawContours
		ctr = np.array(self.contour).reshape((-1,1,2)).astype(np.int32)
		cv2.drawContours(image, [ctr], 0, color, 3)

	def drawROI(self, image, color, thickness = 1):

		cv2.circle(image, self.roi, self.radius, color,thickness)


	def roiColor(self, image):
		# Initialise mask
		maskImage = np.zeros((image.shape[0], image.shape[1]), np.uint8)
		# Draw the ROI circle on the mask
		cv2.circle(maskImage, self.roi, self.radius, (255, 255, 255), -1)
		# Find the average color
		average_raw = cv2.mean(image, mask=maskImage)
		# Need int format so reassign variable
		average = (int(average_raw[0]), int(average_raw[1]), int(average_raw[2]))

		return average

	def roiGray(self, image):
		maskImage = np.zeros((image.shape[0], image.shape[1]), np.uint8)
		cv2.circle(maskImage, self.roi, self.radius, 255, -1)
		average_gray = cv2.mean(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), mask = maskImage)[0]
		return average_gray

	def roiDiff(self, type, pre, cur):
		maskImage = np.zeros((pre.shape[0], pre.shape[1]), np.uint8)
		cv2.circle(maskImage, self.roi, self.radius, (255, 255, 255), -1)
		if type == 'color':
			p = pre
			c = cur
		elif type == 'gray':
			p = cv2.cvtColor(pre, cv2.COLOR_BGR2GRAY)
			c = cv2.cvtColor(cur, cv2.COLOR_BGR2GRAY)
		else:
			print("Wrong type. color or gray")
		
		circle_p = np.zeros_like(p)
		circle_c = np.zeros_like(c)
		circle_p[maskImage == 255] = p[maskImage == 255]
		circle_c[maskImage == 255] = c[maskImage == 255]
		imgDiff = cv2.absdiff(circle_c, circle_p)
		#cv2.imshow('roidiff', imgDiff)
		#ret, th = cv2.threshold(imgDiff, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
		#ret2, th2 = cv2.threshold(th, ret+5, 255, cv2.THRESH_BINARY)
		diff = (cv2.mean(imgDiff, mask = maskImage)[0] + cv2.mean(imgDiff, mask = maskImage)[1] + cv2.mean(imgDiff, mask = maskImage)[2])/3
		#cv2.circle(th2, self.roi, self.radius, 255, 1)		
		#cv2.imshow('sq', th2)
		#cv2.waitKey(0)
		return diff

	def classify(self, image):

		rgb = self.roiColor(image)

		sum = 0
		for i in range(0,3):
			sum += (self.emptyColor[i] - rgb[i])**2


		cv2.putText(image, self.position,self.roi,cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,0),1,cv2.LINE_AA)

