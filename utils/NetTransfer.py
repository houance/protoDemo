import cv2
import numpy as np


class NetTransfer:

    @staticmethod
    def resize(frame):
        return cv2.resize(frame, dsize=(640, 480))

    """
    encode frame to jpg
    basically is turn a numpy array to jpg buffer
    """

    @staticmethod
    def encodeFrame(frame, quality=80):
        ret, frameEncode = cv2.imencode('.jpg', frame, params=[quality])
        if ret:
            return frameEncode
        else:
            return None

    """
    decode an jpg buffer to frame
    """

    @staticmethod
    def decodeFrame(frameEncode):
        nparray = np.asarray(list(frameEncode), dtype='uint8')
        return cv2.imdecode(nparray, cv2.IMREAD_COLOR)

    @staticmethod
    def decodeYuNetPredictServerResult(result):
        nparray = np.asarray(list(result), dtype='uint8')
        return np.reshape(nparray, (-1, 4))
