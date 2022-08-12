import math

import cv2
import numpy as np

from Board import Board
from Line import Line
from Square import Square

debug = True


class BoardRecognition:

	def __init__(self, camera):
		self.cam = camera
		self.square_scale = 50
		self.image = None

	def initializeBoard(self):
		corners = []
		while len(corners) < 121:
			while True:
				self.image = self.cam.getFrame()
				if cv2.Laplacian(self.image, cv2.CV_64F).var() > 3E8 / (self.image.shape[1] * self.image.shape[0]):
					break

			thresh_image = self.cleanImage()
			mask_image = self.initializeMask(thresh_image)
			edges, color_edges = self.findEdges(mask_image)
			# 旋转线框图像至正位
			# rot_edges, rot_color_edges = self.rotateImg(edges)
			rot_edges, rot_color_edges = edges, color_edges  # 暂不旋转
			horizontal, vertical = self.findLines(rot_edges, rot_color_edges)
			corners = self.findCorners(horizontal, vertical, rot_color_edges)
		squares = self.findSquares(corners, self.image)
		board = Board(squares)
		return board

	def cleanImage(self):
		gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
		blur = cv2.GaussianBlur(gray, (17, 17), 0)
		ret1, th1 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
		ret2, th2 = cv2.threshold(blur, ret1 - 20, 255, cv2.THRESH_BINARY)
		auto_thresh = th2

		if debug:
			cv2.imshow("Auto Thresholding", auto_thresh)
			cv2.waitKey(0)
			cv2.destroyAllWindows()

		return auto_thresh

	def initializeMask(self, thresh_image):
		contours, hierarchy = cv2.findContours(thresh_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		image_contours = self.image.copy()

		max_ratio = 0
		max_contour = None
		max_area = 0
		for c in range(len(contours)):
			area = cv2.contourArea(contours[c])
			perimeter = cv2.arcLength(contours[c], True)
			ratio = area / perimeter
			if ratio > max_ratio:
				max_contour = contours[c]
				max_ratio = ratio
				# max_perimeter = perimeter
				max_area = area
		self.square_scale = int(np.sqrt(max_area) / 9)
		cv2.drawContours(image_contours, [max_contour], -1, (0, 0, 0), 1)

		if debug:
			# Show image with contours drawn
			cv2.imshow("Chess Boarder", image_contours)
			cv2.waitKey(0)
			cv2.destroyAllWindows()

		chessboardEdge = cv2.convexHull(max_contour)  # 改用更好的凸包

		mask = np.zeros((self.image.shape[0], self.image.shape[1]), 'uint8')
		cv2.fillConvexPoly(mask, chessboardEdge, 255, 1)
		extracted = np.zeros_like(self.image)
		extracted[mask == 255] = self.image[mask == 255]

		if debug:
			# Show image with mask drawn
			cv2.imshow("mask", extracted)
			cv2.waitKey(0)
			cv2.destroyAllWindows()

		return extracted

	@staticmethod
	def findEdges(mask_image):
		edges = cv2.Canny(mask_image, 60, 100, None, 3)

		if debug:
			# Show image with edges drawn
			cv2.imshow("Canny", edges)
			cv2.waitKey(0)
			cv2.destroyAllWindows()

		color_edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
		return edges, color_edges

	def rotateImg(self, edges):
		lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, np.array([]), self.square_scale * 2, self.square_scale * 3)
		a, b, c = lines.shape
		angles = []
		for i in range(a):
			[[x1, y1, x2, y2]] = lines[i]
			ang_newLine = Line(x1, x2, y1, y2)
			angles.append(ang_newLine.get_angle())

		avg_rot_angle = np.mean(angles)
		print('average rotation angle: ', avg_rot_angle)

		RM = cv2.getRotationMatrix2D((edges.shape[1] // 2, edges.shape[0] // 2), avg_rot_angle, 1.0)
		rot_img = cv2.warpAffine(edges, RM, (edges.shape[1], edges.shape[0]))
		rot_img = np.array(rot_img, np.uint8)
		rot_bgr = cv2.cvtColor(rot_img, cv2.COLOR_GRAY2BGR)
		return rot_img, rot_bgr

	def findLines(self, edges, color_edges):
		lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, np.array([]), self.square_scale * 2, self.square_scale * 3)
		a, b, c = lines.shape
		for i in range(a):
			cv2.line(color_edges, (lines[i][0][0], lines[i][0][1]), (lines[i][0][2], lines[i][0][3]), (0, 255, 0), 2,
					 cv2.LINE_AA)

		if debug:
			# Show image with lines drawn
			cv2.imshow("Lines", color_edges)
			cv2.waitKey(0)
			cv2.destroyAllWindows()

		horizontal = []
		vertical = []
		for i in range(a):
			[[x1, y1, x2, y2]] = lines[i]
			newLine = Line(x1, x2, y1, y2)
			if newLine.orientation == 'horizontal':
				horizontal.append(newLine)
			else:
				vertical.append(newLine)

		return horizontal, vertical

	def findCorners(self, horizontal, vertical, color_edges):
		corners = []
		for v in vertical:
			for h in horizontal:
				s1, s2 = v.find_intersection(h)
				corners.append([s1, s2])

		dedupeCorners = []
		for c in corners:
			matchingFlag = False
			for d in dedupeCorners:
				if math.sqrt((d[0] - c[0]) * (d[0] - c[0]) + (d[1] - c[1]) * (d[1] - c[1])) < self.square_scale * 0.3:
					matchingFlag = True
					break
			if not matchingFlag:
				dedupeCorners.append(c)

		for d in dedupeCorners:
			cv2.circle(color_edges, (d[0], d[1]), 10, (0, 0, 255))

		if debug:
			# Show image with corners circled
			cv2.imshow("Corners", color_edges)
			cv2.waitKey(0)
			cv2.destroyAllWindows()

		return dedupeCorners

	def findSquares(self, corners, color_edges):
		corners.sort(key=lambda x: x[0])
		rows = [[], [], [], [], [], [], [], [], [], [], []]
		r = 0
		size = 11
		for c in range(0, size ** 2):
			if c > 0 and c % size == 0:
				r = r + 1

			rows[r].append(corners[c])

		letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
		numbers = ['1', '2', '3', '4', '5', '6', '7', '8']
		Squares = []

		for r in rows:
			r.sort(key=lambda y: y[1])

		for r in range(0, 8):
			for c in range(0, 8):
				c1 = rows[r + 1][c + 1]
				c2 = rows[r + 1][c + 1 + 1]
				c3 = rows[r + 1 + 1][c + 1]
				c4 = rows[r + 1 + 1][c + 1 + 1]

				position = letters[r] + numbers[7 - c]
				newSquare = Square(color_edges, c1, c2, c3, c4, position, self.square_scale)
				newSquare.draw(color_edges, (0, 0, 255), 2)
				newSquare.drawROI(color_edges, (255, 0, 0), 2)
				newSquare.classify(color_edges)
				Squares.append(newSquare)

		if debug:
			# Show image with squares and ROI drawn and position labelled
			cv2.imshow("Squares", color_edges)
			cv2.waitKey(0)
			cv2.destroyAllWindows()

		return Squares
