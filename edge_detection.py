import os.path
import matplotlib.pyplot as plt

import cv2
import numpy as np


class EdgeDetection():
    lane_lines = []

    def __init__(self):
        pass

    def get_direction(self, frame):
        left = []
        right = []

        # Error check needed for when no lane lines are present
        if EdgeDetection.lane_lines is not None:
            left = EdgeDetection.lane_lines[0][0]
            right = EdgeDetection.lane_lines[1][0]

        # Finding the center of the frame for "center line steering"
        center = int(frame.shape[1]) / 2

        # Checking the position of the Hough Transformation lines - returning direction code
        if len(left) > 0 and left[2] > center and left[2] != 6479999:
            return 3
        elif len(right) > 0 and right[2] < center:
            return 2

        return 1

    @staticmethod
    def process_video(self, frame, is_demo):
        masked = adjust_contrast(frame)
        can_img = image_alteration(masked)

        cropped = region(can_img, is_demo)

        lines = cv2.HoughLinesP(cropped, 2, np.pi / 180, 10, np.array([]), minLineLength=100, maxLineGap=4)

        computed_lines = find_best_fit_lines(frame, lines)
        EdgeDetection.lane_lines = computed_lines

        line_img = drawing_lines(frame, computed_lines)

        image_with_steering = draw_steering(frame)

        lane_detection = cv2.addWeighted(frame, 0.5, line_img, 1, 1)

        steering = cv2.addWeighted(frame, 0, image_with_steering, 1, 0)

        steering_with_lane_detection = cv2.addWeighted(steering, 0.8, lane_detection, 1, 0)

        return steering_with_lane_detection

    @staticmethod
    # preparing AI training data
    def ai_process_video(self, frame):
        height = frame.shape[0]
        img = frame[int(height / 2):, :, :]
        img = cv2.cvtColor(img, cv2.COLOR_RGB2YUV)
        img = cv2.GaussianBlur(img, (5, 5), 0)
        img = cv2.resize(img, (200, 66))
        img = img.reshape(1, 66, 200, 3)
        img = img / 255

        return img

# Adjusting image for Canny Edge Detection Algorithm
def image_alteration(i):
    gray = cv2.cvtColor(i, cv2.COLOR_BGR2GRAY)
    gaus_blur = cv2.GaussianBlur(gray, (5, 5), 0)
    canny = cv2.Canny(gaus_blur, 100, 250)

    return canny

# Adjusting contrast for better lane detection
def adjust_contrast(i):
    brightness = 50
    contrast = 250
    img = np.int16(i)
    adjusted = img * (contrast / 127 + 1) - contrast + brightness
    clipped = np.clip(adjusted, 0, 255)
    clipped = np.uint8(clipped)

    return clipped

# Defining a region for best edge detection success - a different region is defined for the demo video
def region(i, is_demo):
    h = i.shape[0]
    w = i.shape[1]
    mask = np.zeros_like(i)
    if is_demo:
        isolate_shape = np.array([[(150, 300), (275, 200), (350, 200), (525, 325)]], np.int32)
    else:
        isolate_shape = np.array([[(0, h / 2), (w, h / 2), (w, h), (0, h)]], np.int32)

    cv2.fillPoly(mask, isolate_shape, color=(255, 0, 0))
    masked = cv2.bitwise_and(i, mask)

    return masked

# Drawing Hough Transformation lines on the screen for debugging and visualization purposes
def drawing_lines(i, l):
    line_img = np.zeros_like(i)

    if l is not None:
        for line in l:
            for x1, y1, x2, y2 in line:
                cv2.line(line_img, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
    return line_img

# Helper function to get best fit line coordinates of frame instance - error check needed for slope undefined instance
def find_line_coordinates(i, l):
    try:
        slope, intercept = l
    except TypeError:
        slope, intercept = 0.0001, 0

    y1 = int(i.shape[0])
    y2 = int(y1 * (3 / 5))
    x1 = int((y1 - intercept) // slope)
    x2 = int((y2 - intercept) // slope)

    return [[x1, y1, x2, y2]]

# Using Canny Edge Detection and Hough Transformation to determine best fit lines in frame
def find_best_fit_lines(i, l):
    left = []
    right = []

    if l is None:
        return None
    for line in l:
        for x1, y1, x2, y2 in line:
            fit = np.polyfit((x1, x2), (y1, y2), 1)
            slope = fit[0]
            intercept = fit[1]

            if slope < 0:
                left.append((slope, intercept))
            else:
                right.append((slope, intercept))
    left_average = np.average(left, axis=0)
    right_average = np.average(right, axis=0)
    left_line = find_line_coordinates(i, left_average)
    right_line = find_line_coordinates(i, right_average)

    averaged = [left_line, right_line]

    return averaged

# Drawing steering line on the screen
def draw_steering(i):
    steer_img = np.zeros_like(i)
    h = i.shape[0]
    w = i.shape[1]

    x1 = int(w / 2)
    x2 = int(w / 2)
    y1 = int(h)
    y2 = int(h / 2)

    cv2.line(steer_img, (x1, y1), (x2, y2), (0, 0, 255), 5)

    return steer_img
