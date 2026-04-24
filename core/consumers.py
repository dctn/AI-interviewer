from channels.generic.websocket import AsyncWebsocketConsumer
import json
import numpy as np
import cv2
import base64


import mediapipe as mp

from core.detection import Detection
from core.iris_calibration import IrisCalibration



class CheatingConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.calibration = IrisCalibration(50*3)
        self.detection = Detection()
        await self.accept()
        print("Connected!")

    async def receive(self, text_data):
        data = json.loads(text_data)
        frame_data = data['frame']

        # Decode base64 → image
        img_bytes = base64.b64decode(frame_data.split(',')[1])
        np_arr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)


        detect = self.detection.detector(frame,self.calibration)

        #handle no face
        if not detect["face"]:
            await self.send(text_data=json.dumps({
                "x": None,
                "y": None
            }))
            return

        await self.send(text_data=json.dumps(
            detect
        ))

    async def disconnect(self, close_code):
        print("Disconnected")
