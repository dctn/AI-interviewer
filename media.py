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


smooth_ratio   = 0.5
smooth_v_ratio = 0.5
ALPHA = 0.25
DEAD = 0.03

# %%
"""
# calibration technique
- collect sample ratio,v_ratio in each direction or label
- avg both ratios
- calculate threshold value for each direction with defind formula

```
center_h = 0.50   (where your iris sits looking straight)
left_h   = 0.20   (where your iris sits looking far left)

gap = 0.50 - 0.20 = 0.30   (full travel distance)

threshold = 0.50 - (0.30 * 0.95)
          = 0.50 - 0.285
          = 0.215
```

## (plan changed bcs of low accuracy)
- calculate ratio threshold value by percentile of each sample
```
left samples  → find where they END   (85th percentile)
center samples → find where they START (15th percentile)

threshold = (left's end + center's start) / 2
          = midpoint of the gap between them

center samples: [0.45, 0.46, 0.47, 0.50, 0.51]
left samples:   [0.18, 0.19, 0.20, 0.22, 0.30]

left's 85th percentile   = 0.28   ← where left dist ends
center's 15th percentile = 0.46   ← where center dist starts

left_thresh = (0.28 + 0.46) / 2
            = 0.74 / 2
            = 0.37

LEFT dist ends here
        ↓
[0.18..0.28]        [0.46..0.51]
              ↑  ↑
           gap  center starts here
              ↑
           0.37  ← threshold sits in the middle of the gap
```


"""

# %%
class IrisCalibration:
    def __init__(self,):

        self.points = None
        self.samples = {}
        self.thresholds = {}
        self.is_calibrated = False
        self.n_sample = 50*6
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
            accuracy,report = self.calibration_accuracy()
            self.is_calibrated = True
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


    def percentile(self, data, p):
        sorted_data = sorted(data)
        idx = (p / 100) * (len(sorted_data) - 1)
        lo  = int(idx)
        hi  = min(lo + 1, len(sorted_data) - 1)
        return sorted_data[lo] + (sorted_data[hi] - sorted_data[lo]) * (idx - lo)


    def calculate_threshold(self):
        left_h   = [r for r, _ in self.points['left']['samples']]
        right_h  = [r for r, _ in self.points['right']['samples']]
        center_h = [r for r, _ in self.points['center']['samples']]
        top_v    = [v for _, v in self.points['top']['samples']]
        bottom_v = [v for _, v in self.points['bottom']['samples']]
        center_v = [v for _, v in self.points['center']['samples']]




        self.thresholds = {
            'left_thresh':  (self.percentile(left_h,   85) + self.percentile(center_h, 15)) / 2,
            'right_thresh': (self.percentile(center_h, 85) + self.percentile(right_h,  15)) / 2,
            'top_thresh':   (self.percentile(top_v,    85) + self.percentile(center_v, 15)) / 2,
            'down_thresh':  (self.percentile(center_v, 85) + self.percentile(bottom_v, 15)) / 2,
        }
        return self.thresholds

    def calibration_accuracy(self):
        true_points = {
            'center':('center','center'),
            'left':('left','center'),
            'right':('right','center'),
            'top':('center','top'),
            'bottom':('center','bottom'),
        }
        correct = 0
        label_report = {}
        total = 0

        for point in self.points:
            points_samples = self.points[point]['samples']
            label_correct = 0
            true_h,true_v = true_points[point]
            threshold_values = self.thresholds
            for ratio,v_ratio in points_samples:
                total += 1

                if ratio < threshold_values['left_thresh']:
                    pred_h = 'left'
                elif ratio > threshold_values['right_thresh']:
                    pred_h = 'right'
                else:
                    pred_h = 'center'

                if v_ratio < threshold_values['top_thresh']:
                    prev_v = 'top'
                elif v_ratio > threshold_values['down_thresh']:
                    prev_v = 'bottom'
                else:
                    prev_v = 'center'

                if true_h == pred_h and true_v == prev_v:
                    label_correct += 1

            label_report[point] = label_correct
            correct += label_correct

        accuracy = (correct / total) * 100
        print(f'accuracy {accuracy}%')
        print(label_report)
        return accuracy, label_report



# %%
# # for i in calibration.points:
# print(sum([i for i,_ in calibration.points['center']['samples']]) / len([i for i,_ in calibration.points['center']['samples']]))


# %%
cam = cv2.VideoCapture(0)

calibration = IrisCalibration()
threshold_values = None

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

            smooth_ratio   = ALPHA * ratio   + (1 - ALPHA) * smooth_ratio
            smooth_v_ratio = ALPHA * v_ratio + (1 - ALPHA) * smooth_v_ratio

            calibration_values = calibration.collect(frame,smooth_ratio,smooth_v_ratio)

            if calibration_values is not None:
                threshold_values = calibration_values

            if calibration.is_calibrated and threshold_values is not None:

                if smooth_ratio < threshold_values['left_thresh'] - DEAD:
                    direction = 'left'
                elif smooth_ratio > threshold_values['right_thresh'] + DEAD:
                    direction = 'right'
                elif threshold_values['left_thresh'] + DEAD < smooth_ratio < threshold_values['right_thresh'] - DEAD:
                    direction = 'center'
                else:
                    direction = None   # ambiguous — skip this frame

                if smooth_v_ratio < threshold_values['top_thresh'] - DEAD:
                    v_direction = 'up'
                elif smooth_v_ratio > threshold_values['down_thresh'] + DEAD:
                    v_direction = 'down'
                elif threshold_values['top_thresh'] + DEAD < smooth_v_ratio < threshold_values['down_thresh'] - DEAD:
                    v_direction = 'center'
                else:
                    v_direction = None

                cv2.putText(frame, f"{direction}--{v_direction}: ", (30, 40), cv2.FONT_ITALIC,1, (0,0,255), 2)
                cv2.putText(frame, f"{round(ratio,2)}--{round(v_ratio,2)}:", (30, 80), cv2.FONT_ITALIC,1, (0,0,255), 2)


                if direction != 'center' or v_direction != 'center':
                    # logger((direction, v_direction),(ratio,v_ratio))
                    cv2.putText(frame, 'cheating pannada loosu cutie', (w//2,h//2), cv2.FONT_ITALIC,1, (0,0,255), 2)

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
