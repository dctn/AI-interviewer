# %%
import cv2
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import mediapipe as mp

# %%
base = python.BaseOptions(model_asset_path='face_landmarker.task')
options = vision.FaceLandmarkerOptions(
    base_options=base,
    num_faces=1,
)

detector = vision.FaceLandmarker.create_from_options(options)

# %%
left_iris = 468
right_iris = 473
center_iris = 470

# %%
"""
### basic
"""

# %%
# video_cam = cv2.VideoCapture(0)
#
# while video_cam:
#     ret, frame = video_cam.read()
#     frame = cv2.flip(frame, 1)
#     h,w = frame.shape[:2]
#
#     rbg_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#
#     result = detector.detect(mp.Image(image_format=mp.ImageFormat.SRGB,data=rbg_frame))
#
#     if result.face_landmarks:
#         lm = result.face_landmarks[0]
#         left_iris_x, left_iris_y = int(lm[left_iris].x *w), int(lm[left_iris].y * h)
#         right_iris_x, right_iris_y = int(lm[right_iris].x *w), int(lm[right_iris].y * h)
#
#         cv2.circle(frame, (left_iris_x, left_iris_y), 5, (0, 0, 255), -1)
#         cv2.circle(frame, (right_iris_x, right_iris_y), 5, (0, 255, 0), -1)
#
#
#     cv2.imshow(winname='test',mat=frame)
#
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
#
# # print(lm)
# video_cam.release()
# cv2.destroyAllWindows()

# %%
"""
### iris tracker

```
LEFT corner ←——[iris]————→ RIGHT corner

ratio = (iris_x - left_corner_x) / (right_corner_x - left_corner_x)


inner_x = 200px   (landmark 133)
outer_x = 300px   (landmark 33)
iris_x  = 220px   (landmark 468)

ratio = (220 - 200) / (300 - 200)
              = 20 / 100
      = 0.20  → looking LEFT
```
"""

# %%
import random
random.seed(0)
def generate_random_color():
    return random.randint(0,255),random.randint(0,255),random.randint(0,255)

# %%
import csv, time
def logger(type,value):
    with open('log.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow([
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            type,
            value])

# %%
# import tkinter as tk
#
# def get_screen_size(input_frame):
#
#     return screen_CX, screen_CY

# %%
inner = 133 #right
outer = 33 #left
left_iris = 468
top = 10
bottom = 152
ratios = []

generate_random_color()

# %%
"""
# calibration technique
- collect sample ratio,v_ratio in each direction or label
- avg both ratios
- calculate threshold value for each direction with defind formula
![formula](threshold_formula_explained.svg)

```
center_h = 0.50   (where your iris sits looking straight)
left_h   = 0.20   (where your iris sits looking far left)

gap = 0.50 - 0.20 = 0.30   (full travel distance)

threshold = 0.50 - (0.30 * 0.95)
          = 0.50 - 0.285
          = 0.215
```
"""

# %%
class IrisCalibration:
    def __init__(self,):

        self.points = None
        self.samples = {}
        self.thresholds = {}
        self.is_calibrated = False
        self.n_sample = 5
        self.current_idx = 0

    def get_points(self,input_frame):
        screen_h, screen_w = input_frame.shape[0], input_frame.shape[1]
        screen_CX = screen_w // 2
        screen_CY = screen_h // 2
        points = {
            'center':{
                'point':(screen_CX, screen_CY),
                'samples':[]
            },
            'left':{
                'point':(50, screen_CY),
                'samples':[]
            },
            'right':{
                'point':(screen_w - 150, screen_CY),
                'samples':[]
            },
            'top':{
                'point':(screen_CX, 50),
                'samples':[]
            },
            'bottom':{
                'point':(screen_CX, screen_h - 50),
                'samples':[]
            }
        }

        return points

    def collect(self,input_frame,ratio,v_ratio):
        if self.points is None:
            self.points = self.get_points(input_frame)

        if self.current_idx >= len(self.points):
            # TODO: calculate_threshold
            threshold_values = self.calculate_threshold()
            self.calibration_accuracy()

            return threshold_values

        labels = [label for label in self.points.keys()]
        current_point = self.points[labels[self.current_idx]]

        text_point = 0 if self.current_idx == 0 else self.current_idx-1

        #collecting samples
        cv2.putText(input_frame, f"look at {labels[self.current_idx]} circle: ", self.points[labels[text_point]]['point'], cv2.FONT_ITALIC,1, (0,0,255), 2)
        cv2.circle(input_frame,current_point['point'],5,(0,0,255),-1)

        if len(current_point['samples']) < self.n_sample:
            current_point['samples'].append((ratio,v_ratio))
            cv2.putText(input_frame, f"{len(current_point['samples'])}: ", (30, 40), cv2.FONT_ITALIC,1, (0,0,255), 2)
        elif len(current_point['samples']) >= self.n_sample:
            self.current_idx += 1





    def ratio_mean(self,label):
        data = self.points[label]['samples']
        ratio_avg = sum(label_ratio for label_ratio,_ in data) / len(data)
        v_ratio_avg = sum(i for _,i in data) / len(data)
        return ratio_avg, v_ratio_avg

    def calculate_threshold(self):
        center_h,center_v = self.ratio_mean('center')
        left_h,left_v = self.ratio_mean('left')
        right_h,right_v = self.ratio_mean('right')
        top_h,top_v = self.ratio_mean('top')
        bottom_h,bottom_v = self.ratio_mean('bottom')

        buf = 0.05
        v_buf = 0.30
        self.thresholds = {
            'left_thresh':  center_h - (center_h - left_h)  * (1 - buf),
            'right_thresh': center_h + (right_h - center_h) * (1 - buf),
            'up_thresh':    center_v - (center_v - top_v)   * (1 - v_buf),
            'down_thresh':  center_v + (bottom_v - center_v)   * (1 - v_buf),
        }
        # self.is_calibrated = True
        return self.thresholds

    def calibration_accuracy(self):
        true_points = {
            'center':('center','center'),
            'left':('left','center'),
            'right':('right','center'),
            'top':('center','top'),
            'down':('center','bottom'),
        }
        correct = 0
        label_report = {}

        for point in self.points:
            points_samples = self.points[point]['samples']
            label_correct = 0
            true_h,true_v = true_points[point]
            threshold_values = self.thresholds
            for ratio,v_ratio in points_samples:

                if ratio < threshold_values['left_thresh']:
                    pred_h = 'left'
                elif ratio > threshold_values['right_thresh']:
                    pred_h = 'right'
                else:
                    pred_h = 'center'

                if v_ratio < threshold_values['top_thresh']:
                    prev_v = 'top'
                elif v_ratio > threshold_values['down_thresh']:
                    prev_v = 'down'
                else:
                    prev_v = 'center'

                if true_h == pred_h and true_v == prev_v:
                    label_correct += 1

            label_report[point] = label_correct

        accuracy = (correct / self.n_sample) * 100
        print(f'accuracy {accuracy}%')
        print(label_report)
        return accuracy, label_report



# %%
# # for i in calibration.points:
# print(sum([i for i,_ in calibration.points['center']['samples']]) / len([i for i,_ in calibration.points['center']['samples']]))


# %%
cam = cv2.VideoCapture(0)

calibration = IrisCalibration()

while cam:
    try:
        ret, frame = cam.read()
        h,w = frame.shape[:2]
        frame = cv2.flip(frame, 1)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        result = detector.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame))

        if result.face_landmarks:
            ff = result.face_landmarks[0]
            left_conor = ff[outer].x
            right_conor =  ff[inner].x
            left_iris_post =  ff[left_iris].x

            top_iris_post = ff[top].y
            bottom_iris_post = ff[bottom].y
            v_left_iris_post =  ff[left_iris].y


            ratio = (left_iris_post - left_conor) / ((right_conor - left_conor)  + 1e-6)
            v_ratio = (v_left_iris_post - top_iris_post) / (bottom_iris_post - top_iris_post + 1e-6)

            calibration_values = calibration.collect(frame,ratio,v_ratio)

            if calibration.is_calibrated:
                if ratio < calibration_values['left_thresh']:
                    direction = 'left'
                elif ratio > calibration_values['right_thresh']:
                    direction = 'right'
                else:
                    direction = 'center'

                if v_ratio < calibration_values['up_thresh']:
                    v_direction = 'up'
                elif v_ratio > 0.31:
                    v_direction = 'down'
                else:
                    v_direction = 'center'


                cv2.putText(frame, f"{direction}--{v_direction}: ", (30, 40), cv2.FONT_ITALIC,1, (0,0,255), 2)
                cv2.putText(frame, f"{round(ratio,2)}--{round(v_ratio,2)}:", (30, 80), cv2.FONT_ITALIC,1, (0,0,255), 2)


                if direction != 'center' or v_direction != 'center':
                    logger((direction, v_direction),(ratio,v_ratio))
                    cv2.putText(frame, 'cheating pannada loosu kuthi', (w//2,h//2), cv2.FONT_ITALIC,1, (0,0,255), 2)
                for face_landmarks in [left_iris, top, bottom, inner, outer]:
                    cv2.circle(frame, (int(ff[face_landmarks].x*w), int(ff[face_landmarks].y*h)), 5, generate_random_color(), -1)


            elif len(result.face_landmarks) < 1:
                cv2.putText(frame, f"No face detected", (30, 80), cv2.FONT_ITALIC,1, (0,0,255), 2)



        cv2.imshow('test',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    except Exception as e:
        print(e)
        break

cam.release()
cv2.destroyAllWindows()

# %%
