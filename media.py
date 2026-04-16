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

LEFT_EYE_TOP    = 159
LEFT_EYE_BOTTOM = 145

ratios = []

generate_random_color()


smooth_ratio   = None
smooth_v_ratio = None
smooth_ear = None
smooth_head_pos = None
ALPHA = 0.25

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
        self.n_sample = 50*3
        self.current_idx = 0

    def get_points(self,input_frame):
        screen_h, screen_w = input_frame.shape[0], input_frame.shape[1]
        screen_CX = screen_w // 2
        screen_CY = screen_h // 2
        points = {
            'center':{
                'point':(screen_CX, screen_CY),
                'samples':[],
                'other_samples':[]
            },
            'left':{
                'point':(50, screen_CY),
                'samples':[],
                'other_samples':[]
            },
            'right':{
                'point':(screen_w - 150, screen_CY),
                'samples':[],
                'other_samples':[]
            },
            'top':{
                'point':(screen_CX, 50),
                'samples':[],
                'other_samples':[]
            },
            'bottom':{
                'point':(screen_CX, screen_h - 50),
                'samples':[],
                'other_samples':[]
            }
        }

        return points

    def collect(self,input_frame,ratio,v_ratio,ear,head_pos):
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
            current_point['samples'].append((ratio,v_ratio,ear,head_pos))
            cv2.putText(input_frame, f"{len(current_point['samples'])}: ", (30, 40), cv2.FONT_ITALIC,1, (0,0,255), 2)
        elif len(current_point['samples']) >= self.n_sample:
            self.current_idx += 1



    def ratio_mean(self,label,sample='samples'):
        data = self.points[label][sample]
        ratio_avg = sum(label_ratio for label_ratio,_,_,_ in data) / len(data)
        v_ratio_avg = sum(i for _,i,_,_ in data) / len(data)

        ear_avg = sum(ear for _,_,ear,_ in data) / len(data)
        head_pos_avg = sum(head for _,_,_,head in data) / len(data)
        return ratio_avg, v_ratio_avg, ear_avg,head_pos_avg

    def calculate_threshold(self):
        center_h,center_v,center_ear_avg,center_head_pos_avg = self.ratio_mean('center')
        left_h,left_v,_,_ = self.ratio_mean('left')
        right_h,right_v,_,_ = self.ratio_mean('right')
        _,top_v,_,top_head_pos_avg = self.ratio_mean('top')
        _,bottom_v,_,bottom_head_pos_avg = self.ratio_mean('bottom')

        head_pitch_top = abs(center_head_pos_avg - top_head_pos_avg)
        head_pitch_bottom = abs(center_head_pos_avg - bottom_head_pos_avg)


        buf = 0.05
        v_buf = 0.30
        self.thresholds = {
            'left_thresh':  center_h - (center_h - left_h)  * (1 - buf),
            'right_thresh': center_h + (right_h - center_h) * (1 - buf),
            'top_thresh':    center_v - (center_v - top_v)   * (1 - v_buf),
            'down_thresh':  center_v + (bottom_v - center_v)   * (1 - v_buf),
            'ear_thresh':  center_ear_avg * 0.75,
            'head_pos_thresh': max(head_pitch_top,head_pitch_bottom) * 0.7,
            'center_ratio': center_h,
            'center_v_ratio': center_v,
            'center_head_pos': center_head_pos_avg,
            'center_ear':center_ear_avg,
        }
        # self.is_calibrated = True
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
            for ratio,v_ratio,ear,head_pos in points_samples:
                total += 1

                score = fusion_score(ratio,v_ratio,ear,head_pos,self.thresholds)

                if point == 'center' and score < 0.4:
                    label_correct += 1
                elif point != 'center' and score < 0.6:
                    label_correct += 1

            label_report[point] = label_correct
            correct += label_correct

        accuracy = (correct / total) * 100
        print(f'accuracy {accuracy}%')
        print(label_report)
        return accuracy, label_report


# %%
import math
def compute_ear(ff):
    vertical   = abs(ff[LEFT_EYE_TOP].y - ff[LEFT_EYE_BOTTOM].y)
    horizontal = abs(ff[outer].x - ff[inner].x)
    return vertical / (horizontal + 1e-6)

def compute_head_pitch(ff):
    # Simple: how much is the nose displaced from forehead-chin midline
    forehead_y = ff[10].y
    chin_y     = ff[152].y
    nose_y     = ff[1].y

    midline_y = (forehead_y + chin_y) / 2
    face_height = abs(chin_y - forehead_y)

    # Positive = nose above midline = head tilted back
    # Negative = nose below midline = head pitched forward (looking down)
    pitch_ratio = (midline_y - nose_y) / (face_height + 1e-6)
    return pitch_ratio  # range roughly -0.1 to +0.1

# Exponential Moving Average
def ema(current,prev=None,alpha=0.25):
    if prev is None:
        return current
    return alpha * current + (1-alpha) * prev


# Fusion score function
def fusion_score(smooth_ratio,smooth_v_ratio,smooth_ear,smooth_head_pos,threshold_values):
    #horizontal score
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
    ear_drop = max(0,ear_base-smooth_ear)
    ear_score = ear_drop / ear_base
    ear_score = min(1,ear_score)

    #head score
    head_base = threshold_values['center_head_pos']
    head_range = threshold_values['head_pos_thresh']
    head_score = abs(smooth_head_pos - head_base) / head_range

    head_score = min(1,head_score)

    final_fusion_score = (
        0.30 * h_score +
        0.25 * v_score +
        0.20 * ear_score +
        0.25 * head_score
    )

    return final_fusion_score

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

            v_left_iris_post =  ff[left_iris].y
            left_eyelid_top = ff[LEFT_EYE_TOP].y
            left_eyelid_bottom = ff[LEFT_EYE_BOTTOM].y

            top_head_post = ff[top].y
            bottom_head_post = ff[bottom].y


            ratio = (left_iris_post - left_conor) / ((right_conor - left_conor)  + 1e-6)
            v_ratio = (v_left_iris_post - left_eyelid_top) / (left_eyelid_bottom - left_eyelid_top + 1e-6)
            ear = compute_ear(ff)
            head_pos = compute_head_pitch(ff)

            smooth_ratio = ema(current=ratio,prev=smooth_ratio)
            smooth_v_ratio = ema(current=v_ratio,prev=smooth_v_ratio)
            smooth_ear = ema(current=ear,prev=smooth_ear)
            smooth_head_pos = ema(current=head_pos,prev=smooth_head_pos)

            if calibration.is_calibrated == False:
                calibration_values = calibration.collect(frame,smooth_ratio,smooth_v_ratio,smooth_ear,smooth_head_pos)

            if calibration.is_calibrated:

                detection_score  = fusion_score(smooth_ratio,smooth_v_ratio,smooth_ear,smooth_head_pos,calibration_values)

                # if smooth_ratio < calibration_values['left_thresh']:
                #     direction = 'left'
                # elif smooth_ratio > calibration_values['right_thresh']:
                #     direction = 'right'
                # else:
                #     direction = 'center'
                #
                # if smooth_v_ratio < calibration_values['top_thresh']:
                #     v_direction = 'up'
                # elif smooth_v_ratio > calibration_values['down_thresh']:
                #     v_direction = 'down'
                # else:
                #     v_direction = 'center'

                cv2.putText(frame, f"final score--{detection_score}: ", (30, 40), cv2.FONT_ITALIC,1, (0,0,255), 2)
                # cv2.putText(frame, f"{round(ratio,2)}--{round(v_ratio,2)}:", (30, 80), cv2.FONT_ITALIC,1, (0,0,255), 2)


                logger(detection_score,'no cheating')
                if detection_score > 0.6:
                    logger(detection_score,'cheating')
                    cv2.putText(frame, 'cheating pannada loosu cutie', (w//2,h//2), cv2.FONT_ITALIC,1, (0,0,255), 2)

                for face_landmarks in [left_iris, top, bottom, inner, outer,LEFT_EYE_BOTTOM,LEFT_EYE_TOP]:
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
