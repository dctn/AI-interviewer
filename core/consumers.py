import os

from channels.generic.websocket import AsyncWebsocketConsumer
import json
import numpy as np
import cv2
import base64

from django.conf import settings
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import mediapipe as mp
from core.iris_calibration import IrisCalibration

model_path = os.path.join(settings.BASE_DIR, "core", "face_landmarker.task")
base_options = python.BaseOptions(model_asset_path=model_path)

options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    num_faces=1
)

detector = vision.FaceLandmarker.create_from_options(options)


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()
        print("Connected!")

    async def receive(self, text_data):
        data = json.loads(text_data)
        frame_data = data['frame']

        # Decode base64 → image
        img_bytes = base64.b64decode(frame_data.split(',')[1])
        np_arr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        calibration = IrisCalibration(5)

        detect = self.detector(frame,calibration)
        #handle no face
        if not detect["face"]:
            await self.send(text_data=json.dumps({
                "x": None,
                "y": None
            }))
            return

        await self.send(text_data=json.dumps({
            "x": detect["left_iris_x"],
            "y": detect["left_iris_y"],
            "direction": detect["direction"],
            "v_direction": detect["v_direction"],
            'ratio': detect["ratio"],
            'v_ratio': detect["v_ratio"],
        }))

    async def disconnect(self, close_code):
        print("Disconnected")

    def detector(self, frame,calibration):

        # Convert OpenCV frame → RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )


        result = detector.detect(mp_image)

        if not result.face_landmarks:
            return {
                "face": False
            }

        ff = result.face_landmarks[0]

        inner = 133
        outer = 33
        left_iris = 468
        top = 10
        bottom = 152

        h, w = frame.shape[:2]
        left_conor = ff[outer].x
        right_conor = ff[inner].x
        left_iris_x = ff[left_iris].x

        top_y = ff[top].y
        bottom_y = ff[bottom].y
        left_iris_y = ff[left_iris].y

        ratio = (left_iris_x - left_conor) / ((right_conor - left_conor) + 1e-6)
        v_ratio = (left_iris_y - top_y) / ((bottom_y - top_y) + 1e-6)

        threshold_values = calibration.collect(mp_image)
        if calibration.is_calibrated:
            if ratio < 0.35:
                direction = "left"
            elif ratio > 0.55:
                direction = "right"
            else:
                direction = "center"

            if v_ratio < 0.285:
                v_direction = "up"
            elif v_ratio > 0.31:
                v_direction = "down"
            else:
                v_direction = "center"

            return {
                "face": True,
                "direction": direction,
                "v_direction": v_direction,
                "ratio": float(ratio),
                "v_ratio": float(v_ratio),
                'left_iris_x': float(left_iris_x),
                'left_iris_y': float(left_iris_y),
            }


