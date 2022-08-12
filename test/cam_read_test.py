import cv2

def NewCap(cam):
	for i in range(3):
		ret, frame = cam.read()
	return ret, frame

cam = cv2.VideoCapture(0)

print('0')
ret, frame = cam.read()
print('1')
cv2.imshow('1', frame)
print('11')
cam.release()
cv2.waitKey(0)


cam = cv2.VideoCapture(0)
print('2')
ret, frame = cam.read()
print('22')
cv2.imshow('2', frame)
print('222')
cv2.waitKey(0)

print('3')
ret, frame = NewCap(cam)
cv2.imshow('3', frame)

cv2.waitKey(0)

ret, frame = NewCap(cam)
cv2.imshow('4', frame)

cv2.waitKey(0)

cam.release()



