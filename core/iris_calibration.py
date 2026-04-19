from core.detection import Detection

class IrisCalibration:
    def __init__(self,n_samples):
        self.is_calibrated = False
        self.thresholds = {}
        self.points = None
        self.n_samples = n_samples
        self.current_idx = 0

    def get_points(self,input_frame,):
        screen_h, screen_w = input_frame.shape[0], input_frame.shape[1]
        screen_CX = screen_w // 2
        screen_CY = screen_h // 2
        points = {
            'center': {
                'point': (screen_CX, screen_CY),
                'samples': []
            },
            'left': {
                'point': (150, screen_CY),
                'samples': []
            },
            'right': {
                'point': (screen_w - 150, screen_CY),
                'samples': []
            },
            'top': {
                'point': (screen_CX, 50),
                'samples': []
            },
            'bottom': {
                'point': (screen_CX, screen_h - 70),
                'samples': []
            }
        }

        return points

    def collect(self,input_frame,ratio,v_ratio,ear,head_pos):
        if self.points is None:
            self.points = self.get_points(input_frame)

        if self.current_idx >= len(self.points):
            # calculate_threshold
            threshold_values = self.calculate_threshold()
            accuracy, report = self.calibration_accuracy()
            self.is_calibrated = True
            return [threshold_values, accuracy, report]

        labels = [label for label in self.points.keys()]
        current_point = self.points[labels[self.current_idx]]


        if len(current_point['samples']) < self.n_samples:
            current_point['samples'].append((ratio,v_ratio,ear,head_pos))
            return [current_point['point'],self.current_idx,len(current_point['samples'])]
        elif len(current_point['samples']) >= self.n_samples:
            self.current_idx += 1
            return [current_point['point'], self.current_idx, len(current_point['samples'])]

    def ratio_mean(self, label,sample='samples'):
        data = self.points[label][sample]
        ratio_avg = sum(label_ratio for label_ratio, _, _, _ in data) / len(data)
        v_ratio_avg = sum(i for _, i, _, _ in data) / len(data)

        ear_avg = sum(ear for _, _, ear, _ in data) / len(data)
        head_pos_avg = sum(head for _, _, _, head in data) / len(data)
        return ratio_avg, v_ratio_avg, ear_avg, head_pos_avg

    def calculate_threshold(self):
        center_h,center_v,center_ear_avg,center_head_pos_avg = self.ratio_mean('center')
        left_h,left_v,_,_ = self.ratio_mean('left')
        right_h,right_v,_,_ = self.ratio_mean('right')
        _,top_v,_,top_head_pos_avg = self.ratio_mean('top')
        _,bottom_v,_,bottom_head_pos_avg = self.ratio_mean('bottom')

        head_pitch_top = abs(center_head_pos_avg - top_head_pos_avg)
        head_pitch_bottom = abs(center_head_pos_avg - bottom_head_pos_avg)


        buf = 0.05
        v_buf =  0.25
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

                score = Detection.fusion_score(ratio,v_ratio,ear,head_pos,self.thresholds)

                if point == 'center' and score < 0.4:
                    label_correct += 1
                elif point != 'center' and score >= 0.6:
                    label_correct += 1

            label_report[point] = label_correct
            correct += label_correct

        accuracy = (correct / total) * 100
        print(f'accuracy {accuracy}%')
        print(label_report)
        return accuracy, label_report