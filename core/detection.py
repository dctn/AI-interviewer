import cv2
import mediapipe as mp
import os
from django.conf import settings
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class Detection:
    def __init__(self):

        model_path = os.path.join(settings.BASE_DIR, "core", "face_landmarker.task")
        base_options = python.BaseOptions(model_asset_path=model_path)

        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            num_faces=1
        )

        self.detection = vision.FaceLandmarker.create_from_options(options)
        self.inner = 133
        self.outer = 33
        self.left_iris = 468
        self.top = 10
        self.bottom = 152

        self.LEFT_EYE_TOP = 159
        self.LEFT_EYE_BOTTOM = 145


        self.calibration = None

        self.smooth_ratio = None
        self.smooth_v_ratio = None
        self.smooth_ear = None
        self.smooth_head_pos = None

    def compute_ear(self,ff):
        vertical = abs(ff[self.LEFT_EYE_TOP].y - ff[self.LEFT_EYE_BOTTOM].y)
        horizontal = abs(ff[self.outer].x - ff[self.inner].x)
        return vertical / (horizontal + 1e-6)

    def compute_head_pitch(self,ff):
        # Simple: how much is the nose displaced from forehead-chin midline
        forehead_y = ff[self.top].y
        chin_y = ff[self.bottom].y
        nose_y = ff[1].y

        midline_y = (forehead_y + chin_y) / 2
        face_height = abs(chin_y - forehead_y)

        # Positive = nose above midline = head tilted back
        # Negative = nose below midline = head pitched forward (looking down)
        pitch_ratio = (midline_y - nose_y) / (face_height + 1e-6)
        return pitch_ratio  # range roughly -0.1 to +0.1

    def ema(self,current, prev=None, alpha=0.25):
        if prev is None:
            return current
        return alpha * current + (1 - alpha) * prev

    @staticmethod
    def fusion_score(smooth_ratio, smooth_v_ratio, smooth_ear, smooth_head_pos, threshold_values):
        # horizontal score
        center_h = threshold_values['center_ratio']
        h_range = max(abs(threshold_values['left_thresh'] - center_h),
                      abs(threshold_values['right_thresh'] - center_h))
        h_score = abs(smooth_ratio - center_h) / h_range
        h_score = min(1, h_score)

        # vertical score
        center_v = threshold_values['center_v_ratio']
        v_range = max(abs(threshold_values['top_thresh'] - center_v),
                      abs(threshold_values['down_thresh'] - center_v))
        v_score = abs(smooth_v_ratio - center_v) / v_range
        v_score = min(1, v_score)

        # ear score
        ear_base = threshold_values['ear_thresh']
        ear_drop = max(0, ear_base - smooth_ear)
        ear_score = ear_drop / ear_base
        ear_score = min(1, ear_score)

        # head score
        head_base = threshold_values['center_head_pos']
        head_range = threshold_values['head_pos_thresh']
        head_score = abs(smooth_head_pos - head_base) / head_range

        head_score = min(1, head_score)

        final_fusion_score = (
                0.20 * h_score +
                0.30 * v_score +
                0.25 * ear_score +
                0.25 * head_score
        )

        return final_fusion_score

    def detector(self, frame,calibration):

        # Convert OpenCV frame → RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )


        result = self.detection.detect(mp_image)

        if not result.face_landmarks:
            return {
                "face": False
            }

        ff = result.face_landmarks[0]






        h, w = frame.shape[:2]
        # print(h,w)

        left_conor = ff[self.outer].x
        right_conor = ff[self.inner].x
        left_iris_post = ff[self.left_iris].x

        v_left_iris_post = ff[self.left_iris].y
        left_eyelid_top = ff[self.LEFT_EYE_TOP].y
        left_eyelid_bottom = ff[self.LEFT_EYE_BOTTOM].y


        ratio = (left_iris_post - left_conor) / ((right_conor - left_conor) + 1e-6)
        v_ratio = (v_left_iris_post - left_eyelid_top) / ((left_eyelid_bottom - left_eyelid_top) + 1e-6)
        ear = self.compute_ear(ff)
        head_pos = self.compute_head_pitch(ff)

        self.smooth_ear = self.ema(ear,self.smooth_ear)
        self.smooth_head_pos = self.ema(head_pos,self.smooth_head_pos)
        self.smooth_ratio = self.ema(ratio,self.smooth_ratio)
        self.smooth_v_ratio = self.ema(v_ratio,self.smooth_v_ratio)


        if calibration.is_calibrated == False:
            result = calibration.collect(frame,self.smooth_ratio,self.smooth_v_ratio,self.smooth_ear,self.smooth_head_pos)

            if calibration.is_calibrated:
                self.calibration = result




        if calibration.is_calibrated:

            detection_score = self.fusion_score(self.smooth_ratio, self.smooth_v_ratio, self.smooth_ear, self.smooth_head_pos,
                                           self.calibration[0])

            if detection_score > 0.6:
                is_cheating = True
            else:
                is_cheating = False

            return {
                "face": True,
                'fusion_score': detection_score,
                'is_cheating': is_cheating,
                'left_iris_x': float(left_iris_post ),
                'left_iris_y': float(v_left_iris_post),
                'calibrating': False,
                'accuracy': self.calibration[1],
                'label_report': self.calibration[2]
            }

        else:
            x, y = result[0]

            return {
                "face": True,
                "calibrating": True,
                "point_x": x / w,
                "point_y": y / h,
                'label_idx': result[1],
                'label_sample_collect': result[2]
            }