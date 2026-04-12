# %%
import cv2
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import mediapipe as mp
import csv, time, random

# %%
base = python.BaseOptions(model_asset_path='face_landmarker.task')
options = vision.FaceLandmarkerOptions(base_options=base, num_faces=1)
detector = vision.FaceLandmarker.create_from_options(options)

# %%
random.seed(0)
def generate_random_color():
    return random.randint(0,255), random.randint(0,255), random.randint(0,255)

def logger(type, value):
    with open('log.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), type, value])

# %%
inner     = 133
outer     = 33
left_iris = 468
top       = 10
bottom    = 152

# %%
class IrisCalibration:
    def __init__(self):
        self.points        = None
        self.thresholds    = {}
        self.is_calibrated = False
        self.n_sample      = 100 * 3
        self.current_idx   = 0

    def get_points(self, input_frame):
        h, w = input_frame.shape[:2]
        cx, cy = w // 2, h // 2
        return {
            'center': {'point': (cx,      cy),      'samples': []},
            'left':   {'point': (50,      cy),      'samples': []},
            'right':  {'point': (w - 150, cy),      'samples': []},
            'top':    {'point': (cx,      50),      'samples': []},
            'bottom': {'point': (cx,      h - 50),  'samples': []},
        }

    def collect(self, input_frame, ratio, v_ratio):
        if self.points is None:
            self.points = self.get_points(input_frame)

        labels = list(self.points.keys())

        if self.current_idx >= len(labels):
            threshold_values = self.calculate_threshold()
            accuracy, report = self.calibration_accuracy()
            self.is_calibrated = True
            return threshold_values

        current_label = labels[self.current_idx]
        current_point = self.points[current_label]
        text_point    = 0 if self.current_idx == 0 else self.current_idx - 1

        cv2.putText(input_frame, f"look at {current_label} circle",
                    self.points[labels[text_point]]['point'],
                    cv2.FONT_ITALIC, 1, (0, 0, 255), 2)
        cv2.circle(input_frame, current_point['point'], 5, (0, 0, 255), -1)

        if len(current_point['samples']) < self.n_sample:
            current_point['samples'].append((ratio, v_ratio))
            cv2.putText(input_frame, f"{len(current_point['samples'])}/{self.n_sample}",
                        (30, 40), cv2.FONT_ITALIC, 1, (0, 0, 255), 2)
        else:
            self.current_idx += 1

        return None

    def percentile(self, data, p):
        sorted_data = sorted(data)
        idx = (p / 100) * (len(sorted_data) - 1)
        lo, hi = int(idx), min(int(idx) + 1, len(sorted_data) - 1)
        return sorted_data[lo] + (sorted_data[hi] - sorted_data[lo]) * (idx - lo)

    def calculate_threshold(self):
        # KEY CHANGE: percentile-based thresholds
        # Instead of: mean → formula → threshold  (assumes symmetric distributions)
        # Now:        look at where each direction's distribution actually ends
        #             and place the threshold at the midpoint between neighbours
        #
        # left_thresh  = midpoint between left's 85th pct  and center's 15th pct
        # right_thresh = midpoint between center's 85th pct and right's 15th pct
        # top_thresh   = midpoint between top's 85th pct   and center's 15th pct
        # down_thresh  = midpoint between center's 85th pct and bottom's 15th pct

        left_h   = [r for r, _ in self.points['left']['samples']]
        right_h  = [r for r, _ in self.points['right']['samples']]
        center_h = [r for r, _ in self.points['center']['samples']]
        top_v    = [v for _, v in self.points['top']['samples']]
        bottom_v = [v for _, v in self.points['bottom']['samples']]
        center_v = [v for _, v in self.points['center']['samples']]

        left_thresh  = (self.percentile(left_h,   85) + self.percentile(center_h, 15)) / 2
        right_thresh = (self.percentile(center_h, 85) + self.percentile(right_h,  15)) / 2
        top_thresh   = (self.percentile(top_v,    85) + self.percentile(center_v, 15)) / 2
        down_thresh  = (self.percentile(center_v, 85) + self.percentile(bottom_v, 15)) / 2

        self.thresholds = {
            'left_thresh':  left_thresh,
            'right_thresh': right_thresh,
            'top_thresh':   top_thresh,
            'down_thresh':  down_thresh,
        }
        print(f"\nThresholds: {self.thresholds}")
        return self.thresholds

    def calibration_accuracy(self):
        true_points = {
            'center': ('center', 'center'),
            'left':   ('left',   'center'),
            'right':  ('right',  'center'),
            'top':    ('center', 'top'),
            'bottom': ('center', 'bottom'),
        }
        correct, total, label_report = 0, 0, {}
        t = self.thresholds

        for point, info in self.points.items():
            true_h, true_v = true_points[point]
            label_correct  = 0
            for ratio, v_ratio in info['samples']:
                total += 1
                pred_h = 'left'   if ratio   < t['left_thresh']  else \
                         'right'  if ratio   > t['right_thresh'] else 'center'
                pred_v = 'top'    if v_ratio < t['top_thresh']   else \
                         'bottom' if v_ratio > t['down_thresh']  else 'center'
                if pred_h == true_h and pred_v == true_v:
                    label_correct += 1
            label_report[point] = label_correct
            correct += label_correct

        accuracy = (correct / total) * 100
        print(f'accuracy {accuracy:.1f}%')
        print(label_report)
        return accuracy, label_report


# %%
cam         = cv2.VideoCapture(0)
calibration = IrisCalibration()
cal_values  = None

smooth_ratio   = 0.5
smooth_v_ratio = 0.5
ALPHA          = 0.25
DEAD           = 0.03

while cam:
    try:
        ret, frame = cam.read()
        h, w = frame.shape[:2]
        frame = cv2.flip(frame, 1)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result    = detector.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame))

        if result.face_landmarks:
            ff = result.face_landmarks[0]

            left_corner  = ff[outer].x
            right_corner = ff[inner].x
            iris_x       = ff[left_iris].x
            iris_y       = ff[left_iris].y
            top_y        = ff[top].y
            bottom_y     = ff[bottom].y

            raw_ratio   = (iris_x - left_corner) / (right_corner - left_corner + 1e-6)
            raw_v_ratio = (iris_y  - top_y)       / (bottom_y    - top_y       + 1e-6)

            smooth_ratio   = ALPHA * raw_ratio   + (1 - ALPHA) * smooth_ratio
            smooth_v_ratio = ALPHA * raw_v_ratio + (1 - ALPHA) * smooth_v_ratio

            result_val = calibration.collect(frame, smooth_ratio, smooth_v_ratio)
            if result_val is not None:
                cal_values = result_val

            if calibration.is_calibrated and cal_values is not None:
                t = cal_values

                if smooth_ratio < t['left_thresh'] - DEAD:
                    direction = 'left'
                elif smooth_ratio > t['right_thresh'] + DEAD:
                    direction = 'right'
                elif t['left_thresh'] + DEAD < smooth_ratio < t['right_thresh'] - DEAD:
                    direction = 'center'
                else:
                    direction = None

                if smooth_v_ratio < t['top_thresh'] - DEAD:
                    v_direction = 'up'
                elif smooth_v_ratio > t['down_thresh'] + DEAD:
                    v_direction = 'down'
                elif t['top_thresh'] + DEAD < smooth_v_ratio < t['down_thresh'] - DEAD:
                    v_direction = 'center'
                else:
                    v_direction = None

                if direction is not None and v_direction is not None:
                    if direction != 'center' or v_direction != 'center':
                        logger((direction, v_direction), (smooth_ratio, smooth_v_ratio))
                        cv2.putText(frame, 'cheating pannada loosu cutie',
                                    (w//2, h//2), cv2.FONT_ITALIC, 1, (0, 0, 255), 2)

        else:
            cv2.putText(frame, "No face detected", (30, 80), cv2.FONT_ITALIC, 1, (0, 0, 255), 2)

        cv2.imshow('test', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    except Exception as e:
        print(e)
        break

cam.release()
cv2.destroyAllWindows()