import os.path

import cv2
import sys
import serial
from edge_detection import EdgeDetection
import time
from neural_network import CNN
from keras.models import load_model

control_mode = str(sys.argv[1])

cap = 0
if control_mode == 'edge':
    to_arduino = serial.Serial(port='/dev/cu.usbserial-AB0P8TBC', baudrate=9600)

    video = cv2.VideoCapture(1)
    time.sleep(5)

    ed = EdgeDetection()
    while video.isOpened():
        try:
            _, frame = video.read()
            process = ed.process_video(_, frame, False)
            direction = str(ed.get_direction(frame))

            to_arduino.write(str.encode(direction))
            time.sleep(100 / 1000)
            from_arduino = str(to_arduino.readline())

            if from_arduino:
                print(from_arduino)
            direction_translate = ''
            if direction == '1':
                direction_translate = 'straight'
            elif direction == '2':
                direction_translate = 'left'
            elif direction == '3':
                direction_translate = 'right'

            process_with_rpms = cv2.putText(process, 'Direction: ' + direction_translate, (50, 50), cv2.FONT_HERSHEY_TRIPLEX,
                                            1,
                                            (255, 255, 255), 2, cv2.LINE_AA)

            cv2.imshow('frame', process_with_rpms)

            # path = '/Users/matt.scuteri/Desktop/GCU/CST-590/self-driving-dnn/training_data'
            # cv2.imwrite(os.path.join(path, 'frame' + str(cap) + str(direction) + '.jpg'), frame)
            # cap += 1

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        except Exception as e:
            to_arduino.write(str.encode("0"))
            time.sleep(100 / 1000)
            print(e)

elif control_mode == 'learned':
    to_arduino = serial.Serial(port='/dev/cu.usbserial-AB0P8TBC', baudrate=9600)

    video = cv2.VideoCapture(1)
    time.sleep(5)

    ed = EdgeDetection()
    cnn = CNN()

    # cnn.load_training_data()
    model = load_model('./drive_model.h5')
    try:
        while video.isOpened():
            _, frame = video.read()
            process = ed.ai_process_video(_, frame, False)
            direction = str(round(model.predict(process)[0][0]))
            to_arduino.write(str.encode(direction))
            time.sleep(100 / 1000)
            from_arduino = to_arduino.readline()

            if from_arduino:
                print(from_arduino)

            process_with_rpms = cv2.putText(frame, 'Direction: ' + direction, (50, 50), cv2.FONT_HERSHEY_TRIPLEX,
                                            1,
                                            (255, 255, 255), 2, cv2.LINE_AA)

            cv2.imshow('process', process_with_rpms)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:
        to_arduino.write(str.encode("0"))
        time.sleep(100 / 1000)
        print(e)
elif control_mode == "demo_edge":
    video = cv2.VideoCapture('./project_images/demo-video.mov')
    ed = EdgeDetection()
    while video.isOpened():
        try:
            _, frame = video.read()

            if frame is None:
                break

            process = ed.process_video(_, frame, True)
            direction = str(ed.get_direction(frame))

            direction_translate = ''
            if direction == '1':
                direction_translate = 'straight'
            elif direction == '2':
                direction_translate = 'left'
            elif direction == '3':
                direction_translate = 'right'

            process_with_rpms = cv2.putText(process, 'Direction: ' + direction_translate, (50, 50), cv2.FONT_HERSHEY_TRIPLEX,
                                            1,
                                            (255, 255, 255), 2, cv2.LINE_AA)

            cv2.imshow('Edge_Detection', process_with_rpms)

            # path = '/Users/matt.scuteri/Desktop/GCU/CST-590/self-driving-dnn/training_data'
            # cv2.imwrite(os.path.join(path, 'frame' + str(cap) + str(direction) + '.jpg'), frame)
            # cap += 1

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except Exception as e:
            print(e)

elif control_mode == "demo_learn":
    video = cv2.VideoCapture('./project_images/demo-video.mov')

    ed = EdgeDetection()
    cnn = CNN()

    # cnn.load_training_data()
    model = load_model('./drive_model.h5')
    try:
        while video.isOpened():
            _, frame = video.read()
            process = ed.ai_process_video(_, frame)
            direction = str(round(model.predict(process)[0][0]))

            direction_translate = ''
            if direction == '1':
                direction_translate = 'straight'
            elif direction == '2':
                direction_translate = 'left'
            elif direction == '3':
                direction_translate = 'right'

            process_with_rpms = cv2.putText(frame, 'Direction: ' + direction_translate, (50, 50), cv2.FONT_HERSHEY_TRIPLEX,
                                            1,
                                            (255, 255, 255), 2, cv2.LINE_AA)

            cv2.imshow('AI', process_with_rpms)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:
        print(e)
else:
    print('Accepted arguments:\n"edge": run prototype with edge detection\n"learned": run prototype with trained model\n"demo_edge": run edge detection with sample video\n"demo_learned": run trained model with sample videp')

video.release()
cv2.destroyAllWindows()

# to_arduino.write(str.encode("0"))
