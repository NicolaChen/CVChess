import math
from sys import addaudithook
import cv2
from cv2 import adaptiveThreshold
import numpy as np
#import imutils
from Line import Line
from Square import Square
from Board import Board

debug =  True


class board_Recognition:
	'''
	This class handles the initialization of the board. It analyzes
	the empty board finding its border, lines, corners, squares...
	'''

	def __init__(self, camera):
		self.cam = camera
		self.sqscale = 50

	def initialize_Board(self):
		corners = []

		# retake picture until board is initialized properly
		while len(corners) < 121:
			#ret, image = self.cam.takePicture()
			while True:
				image = self.cam.getFrame()
				if cv2.Laplacian(image, cv2.CV_64F).var() > 4E8/(image.shape[1] * image.shape[0]):
					break	
	
			# Binarize the photo
			adaptiveThresh = self.clean_Image(image)

			# Black out all pixels outside the border of the chessboard
			mask = self.initialize_mask(adaptiveThresh, image)

			# Find edges
			edges, colorEdges = self.findEdges(mask)

			# 旋转线框图像至正位
			# rot_edges, rot_color_edges = self.rotateImg(edges)
			rot_edges, rot_color_edges = edges, colorEdges

			# Find lines
			horizontal, vertical = self.findLines(rot_edges, rot_color_edges)

			# Find corners
			corners = self.findCorners(horizontal, vertical, rot_color_edges)

		# Find squares
		squares = self.findSquares(corners, image)

		# create Board
		board = Board(squares)

		return board

	def clean_Image(self, image):
		'''
		Resizes and converts the photo to black and white for simpler analysis
		'''
		# resize image
		# img = imutils.resize(image, width = 400, height = 400)
		
		# Convert to grayscale
		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

		# Setting all pixels above the threshold value to white and those below to black
		# Adaptive thresholding is used to combat differences of illumination in the picture
		# adaptiveThresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 125, 1)
		# 改进：采用模糊后OTSU获得阈值，结合实际实验参数，调整实际阈值
		blur = cv2.GaussianBlur(gray, (17, 17), 0)
		ret1, th1 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
		ret2, th2 = cv2.threshold(blur, ret1-20, 255, cv2.THRESH_BINARY)
		adaptiveThresh = th2

		if debug:
			# Show thresholded image
			cv2.imshow("Adaptive Thresholding", adaptiveThresh)
			cv2.waitKey(0)
			cv2.destroyAllWindows()

		return adaptiveThresh

	def initialize_mask(self, adaptiveThresh, img):
		'''
		Finds border of chessboard and blacks out all unneeded pixels
		'''

		# Find contours (closed polygons)
		contours, hierarchy = cv2.findContours(adaptiveThresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

		# Create copy of original image
		imgContours = img.copy()

		Lratio = 0
		MaxCtr = None
		for c in range(len(contours)):
			# Area
			area = cv2.contourArea(contours[c])
			# Perimenter
			perimeter = cv2.arcLength(contours[c], True)

			# if area > 800000 or perimeter > 7000 or area < 80000 or perimeter < 800:
			# 	continue
			# Filtering the chessboard edge / Error handling as some contours are so small so as to give zero division
			#For test values are 70-40, for Board values are 80 - 75 - will need to recalibrate if change
			#the largest square is always the largest ratio
			#if perimeter > 500 and perimeter < 8000:
			ratio = area / perimeter
			if ratio > Lratio:
				MaxCtr = contours[c]
				Lratio = ratio
				Lperimeter = perimeter
				Larea = area
			#else:
				#pass
		self.sqscale = int(np.sqrt(Larea)/9)
		# Draw contours
		cv2.drawContours(imgContours, [MaxCtr], -1, (0,0,0), 1)
		if debug:
			# Show image with contours drawn
			cv2.imshow("Chess Boarder", imgContours)
			cv2.waitKey(0)
			cv2.destroyAllWindows()

		# Epsilon parameter needed to fit contour to polygon
		epsilon = 0.01 * Lperimeter
		# Approximates a polygon from chessboard edge
		# chessboardEdge = cv2.approxPolyDP(MaxCtr, epsilon, True)
		chessboardEdge = cv2.convexHull(MaxCtr)     #凸包，改进觉得这个更好

		# Create new all black image
		mask = np.zeros((img.shape[0], img.shape[1]), 'uint8')
		# Copy the chessboard edges as a filled white polygon size of chessboard edge
		cv2.fillConvexPoly(mask, chessboardEdge, 255, 1)
		# Assign all pixels that are white (i.e the polygon, i.e. the chessboard)
		extracted = np.zeros_like(img)
		extracted[mask == 255] = img[mask == 255]
		# remove strip around edge
		# extracted[np.where((extracted == [125, 125, 125]).all(axis=2))] = [0, 0, 20]

		if debug:
			# Show image with mask drawn
			cv2.imshow("mask",extracted)
			cv2.waitKey(0)
			cv2.destroyAllWindows()
		return extracted

	def findEdges(self, image):
		'''
		Finds edges in the image. Edges later used to find lines and so on
		'''
	
		# Find edges
		edges = cv2.Canny(image, 60, 100, None, 3)
		if debug:
			#Show image with edges drawn
			cv2.imshow("Canny", edges)
			cv2.waitKey(0)
			cv2.destroyAllWindows()

		# Convert edges image to grayscale
		colorEdges = cv2.cvtColor(edges,cv2.COLOR_GRAY2BGR)

		return edges, colorEdges

	def rotateImg(self, edges):
		'''
		Rotate the image according to edges found before, return rotated GRAY & BGR image
		'''
		lines = cv2.HoughLinesP(edges, 1,  np.pi / 180, 100,np.array([]), self.sqscale*2, self.sqscale*3)
		a,b,c = lines.shape
		angles = []
		for l in range(a):
			[[x1, y1, x2, y2]] = lines[l]
			ang_newLine = Line(x1, x2, y1, y2)
			angles.append(ang_newLine.get_angle())
			
		avg_rot_angle = np.mean(angles)
		print('average rotation angle: ', avg_rot_angle)

		RM = cv2.getRotationMatrix2D((edges.shape[1]//2, edges.shape[0]//2), avg_rot_angle, 1.0)
		rot_img = cv2.warpAffine(edges, RM, (edges.shape[1], edges.shape[0]))
		rot_img = np.array(rot_img, np.uint8)
		rot_bgr = cv2.cvtColor(rot_img, cv2.COLOR_GRAY2BGR)
		return rot_img, rot_bgr

	def findLines(self, edges, colorEdges):
		'''
		Finds the lines in the photo and sorts into vertical and horizontal
		'''
		
		# Infer lines based on edges
		lines = cv2.HoughLinesP(edges, 1,  np.pi / 180, 100,np.array([]), self.sqscale*2, self.sqscale*3)

		# Draw lines
		a,b,c = lines.shape
		for i in range(a):
			cv2.line(colorEdges, (lines[i][0][0], lines[i][0][1]), (lines[i][0][2], lines[i][0][3]), (0,255,0),2,cv2.LINE_AA)

		if  debug:
			# Show image with lines drawn
			cv2.imshow("Lines",colorEdges)
			cv2.waitKey(0)
			cv2.destroyAllWindows()

		# Create line objects and sort them by orientation (horizontal or vertical)
		horizontal = []
		vertical = []
		for l in range(a):
			[[x1,y1,x2,y2]] = lines[l]
			newLine = Line(x1,x2,y1,y2)
			if newLine.orientation == 'horizontal':
				horizontal.append(newLine)
			else:
				vertical.append(newLine)

		return horizontal, vertical

	def findCorners (self, horizontal, vertical, colorEdges):
		'''
		Finds corners at intersection of horizontal and vertical lines.
		'''

		# Find corners (intersections of lines)
		corners = []
		for v in vertical:
			for h in horizontal:
				s1,s2 = v.find_intersection(h)
				corners.append([s1,s2])

		# remove duplicate corners
		dedupeCorners = []
		for c in corners:
			matchingFlag = False
			for d in dedupeCorners:
				if math.sqrt((d[0]-c[0])*(d[0]-c[0]) + (d[1]-c[1])*(d[1]-c[1])) < self.sqscale*0.3:
					matchingFlag = True
					break
			if not matchingFlag:
				dedupeCorners.append(c)

		for d in dedupeCorners:
			cv2.circle(colorEdges, (d[0],d[1]), 10, (0,0,255))


		if debug:
			#Show image with corners circled
			cv2.imshow("Corners",colorEdges)
			cv2.waitKey(0)
			cv2.destroyAllWindows()

		return dedupeCorners

	def findSquares(self, corners, colorEdges):
		'''
		Finds the squares of the chessboard 
		'''

		# sort corners by row
		corners.sort(key=lambda x: x[0])
		rows = [[],[],[],[],[],[],[],[],[],[],[]]
		r = 0
		size = 11
		for c in range(0, size**2):
			if c > 0 and c % size == 0:
				r = r + 1

			rows[r].append(corners[c])

		letters = ['a','b','c','d','e','f','g','h']
		numbers = ['1','2','3','4','5','6','7','8']
		Squares = []
		
		# sort corners by column
		for r in rows:
			r.sort(key=lambda y: y[1])
		
		# initialize squares
		for r in range(0,8):
			for c in range (0,8):
				c1 = rows[r+1][c+1]
				c2 = rows[r+1][c+1 + 1]
				c3 = rows[r+1 + 1][c+1]
				c4 = rows[r+1 + 1][c+1 + 1]

				position = letters[r] + numbers[7-c]
				newSquare = Square(colorEdges, c1, c2, c3, c4, position, self.sqscale)
				newSquare.draw(colorEdges,(0,0,255),2)
				newSquare.drawROI(colorEdges,(255,0,0),2)
				newSquare.classify(colorEdges)
				Squares.append(newSquare)



		if debug:
			#Show image with squares and ROI drawn and position labelled
			cv2.imshow("Squares", colorEdges)
			cv2.waitKey(0)
			cv2.destroyAllWindows()

		return Squares
