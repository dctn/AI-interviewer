class IrisCalibration:
    def __init__(self,n_samples):
        is_calibrated = False
        self.threshold = {}
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
                'point': (50, screen_CY),
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
                'point': (screen_CX, screen_h - 50),
                'samples': []
            }
        }

        return points

    def collect(self,input_frame,ratio,v_ratio):
        if self.points is None:
            self.points = self.get_points(input_frame)

        if self.current_idx >= len(self.points):
            # TODO: calculate_threshold
            threshold_values = self.calculate_threshold()
            accuracy, report = self.calibration_accuracy()
            self.is_calibrated = True
            return threshold_values

        labels = [label for label in self.points.keys()]
        current_point = self.points[labels[self.current_idx]]


        if len(current_point['samples']) < self.n_sample:
            current_point['samples'].append((ratio,v_ratio))
        elif len(current_point['samples']) >= self.n_samples:
            self.current_idx += 1


    def ratio_mean(self,label):
        ratio_data = self.points[label]['samples']
        avg_ratio = sum([i for i,_ in ratio_data]) / len(ratio_data)
        avg_v_ratio = sum([i for _,i in ratio_data]) / len(ratio_data)
        return avg_ratio, avg_v_ratio

    def calculate_threshold(self):
        center_h, center_v = self.ratio_mean('center')
        left_h, left_v = self.ratio_mean('left')
        right_h, right_v = self.ratio_mean('right')
        top_h, top_v = self.ratio_mean('top')
        bottom_h, bottom_v = self.ratio_mean('bottom')

        buf = 0.05
        v_buf = 0.30
        self.threshold = {
            'left_thresh': center_h - (center_h - left_h) * (1 - buf),
            'right_thresh': center_h + (right_h - center_h) * (1 - buf),
            'top_thresh': center_v - (center_v - top_v) * (1 - v_buf),
            'down_thresh': center_v + (bottom_v - center_v) * (1 - v_buf),
        }
        # self.is_calibrated = True
        return self.threshold


    def calibration_accuracy(self):
        true_points = {
            'center': ('center', 'center'),
            'left': ('left', 'center'),
            'right': ('right', 'center'),
            'top': ('center', 'top'),
            'bottom': ('center', 'bottom'),
        }

        correct = 0
        total = 0
        label_report = {}

        for point in self.points.keys():
            label_correct = 0
            for ratio,v_ratio in self.points[point]['samples']:

                if ratio < self.threshold['left_thresh']:
                    pred_direction = 'left'
                elif ratio > self.threshold['right_thresh']:
                    pred_direction = 'right'
                else:
                    pred_direction = 'center'

                if v_ratio > self.threshold['down_thresh']:
                    pred_direction_v = 'top'
                elif v_ratio < self.threshold['up_thresh']:
                    pred_direction_v = 'bottom'
                else:
                    pred_direction_v = 'center'

                if pred_direction == true_points[point][0] and pred_direction_v == true_points[point][1]:
                    label_correct += 1
                total += 1
            correct += label_correct
            label_report[point] = correct
        accuracy = correct / total
        print(f'accuracy {accuracy}%')
        print(label_report)
        return accuracy, label_report