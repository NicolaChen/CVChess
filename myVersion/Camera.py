# import the necessary package
import threading
import time

import cv2


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
            cv2.putText(frame, str(cv2.Laplacian(frame, cv2.CV_64F).var()), (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (255, 0, 0))
            cv2.putText(frame, 'w: ' + str(frame.shape[1]) + ', h: ' + str(frame.shape[0]) + "var: " + str(
                3E8 / (frame.shape[1] * frame.shape[0])), (100, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0))
            cv2.putText(frame, str(cv2.mean(frame)[0] + cv2.mean(frame)[1] + cv2.mean(frame)[2]), (100, 300),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0))
            cv2.imshow("calibration", frame)  # TODO: Figure out how to fix the position of imshow window
            if cv2.waitKey(100) == 27:
                cv2.destroyWindow("calibration")
                break

    def run(self):

        while True:
            self.lock.acquire()
            ret, frame = self.cam.read()
            scale = 0.5  # TODO: Test appropriate scale for 800*600 screen
            SIZE = (int(scale * frame.shape[1]), int(scale * frame.shape[0]))
            self.frame = cv2.resize(frame, SIZE)
            self.lock.release()
            time.sleep(0.1)

    def getFrame(self):

        self.lock.acquire()
        frame = self.frame
        self.lock.release()
        return frame
