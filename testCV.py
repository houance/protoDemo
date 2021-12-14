import cv2
import time

import numpy
from yuNet import Header, Request, Response
from utils.NetTransfer import NetTransfer
from cv.YuNet import YuNet


frame = cv2.imread('/home/protobufDemo/pic.jpg')
jpg = NetTransfer.encodeFrame(frame)
req = Request()

while True:
    req.encodeJpg = jpg
    data = req.SerializeToString()
