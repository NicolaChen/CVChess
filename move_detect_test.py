import cv2
import numpy as np

cam = cv2.VideoCapture(0)
i=0
while True:
	ret, frame = cam.read()
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	mean = cv2.mean(gray)[0]
	print("image_gray_avrg: " + str(mean))
	maskImage = np.zeros((gray.shape[0], gray.shape[1]), np.uint8)
	cv2.circle(maskImage, (700,760), 40, 255, -1)
	average_gray = cv2.mean(gray, mask = maskImage)[0]
	print("circle gray avrg: " + str(average_gray))
	print("DIFF: " + str(average_gray-mean) + "\n")
	cv2.circle(gray, (700,760), 40, 255, 1)
	cv2.imshow('gray', gray)
	if cv2.waitKey(1000)==27:
		break
cam.release()
