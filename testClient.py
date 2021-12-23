import time
import cv2
from client.Client import Client
from cv.YuNet import YuNet

if __name__ == "__main__":
    client = Client('127.0.0.1', 9500, 1)
    yu = YuNet()

    while True:
        start = time.time()
        frame = cv2.imread('./pic.jpg')
        result = client.send(frame)
        yu.visualize(frame, result)
        print('frame rate = ' + str(1/(time.time() - start)))
