import cv2

cam = cv2.VideoCapture(0)
while cam.isOpened():
	ret, frame = cam.read()
	scale = 1
	SIZE = (int(scale * frame.shape[1]), int(scale * frame.shape[0]))
	frame = cv2.resize(frame, SIZE)
	lap = cv2.Laplacian(frame, cv2.CV_64F).var()
	cv2.putText(frame, str(4E8/(frame.shape[1] * frame.shape[0])), (100,100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0))
	cv2.putText(frame, str(lap), (200,200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0))
	cv2.imshow('t', frame)
	if cv2.waitKey(100) == 27:
		break
cam.release()
