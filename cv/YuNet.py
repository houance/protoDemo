import cv2
import numpy as np


class YuNet:
    def __init__(self, path='/home/protobufDemo/model/YuFaceDetectNet.onnx'):
        self.yuNet = cv2.FaceDetectorYN.create(
            model=path,
            config='',
            input_size=(640, 480),
            score_threshold=0.5,
            nms_threshold=0.3,
            top_k=20,
            backend_id=cv2.dnn.DNN_BACKEND_OPENCV,
            target_id=cv2.dnn.DNN_TARGET_CPU
        )

    def predict(self, frame, local=True) -> list:
        cv2.resize(frame, dsize=(640, 480))

        _, faces = self.yuNet.detect(frame)

        if faces is None:
            return []

        if local:
            return faces[:, :4].astype(np.int32)
        else:
            return faces[:, :4].astype(np.int32).flatten()

    @staticmethod
    def visualize(frame, faces):

        if faces is None:
            return None

        for face in faces:
            cv2.rectangle(
                frame,
                (face[0], face[1]),
                (face[0] + face[2], face[1] + face[3]),
                (0, 0, 255),
                2
            )
