import random

import cv2
import os
import sys

import numpy as np
from sklearn import model_selection

from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Lambda, Conv2D
from keras.optimizers import Adam
from keras.callbacks import ModelCheckpoint


class CNN(object):
    def __init__(self):
        self.data_location = os.path.dirname(sys.path[0]) + "/self-driving-car/training_data"
        self.img_data = []
        self.direction = []
    # Retrieve training data from directory and prepare for training
    def load_training_data(self):
        for img in os.listdir(self.data_location):
            img_split = img.split('.')

            if len(img_split[0]) > 0:
                direction_slice = img_split[0][-1]

                self.direction.append(int(direction_slice))
                img = cv2.imread(self.data_location + '/' + img)
                height = img.shape[0]
                img = img[int(height / 2):, :, :]
                img = cv2.cvtColor(img, cv2.COLOR_RGB2YUV)
                img = cv2.GaussianBlur(img, (5, 5), 0)
                img = cv2.resize(img, (200, 66))
                img = img / 255

                self.img_data.append(img)
                if random.randint(0, 1) == 1:
                    aug_img = img_augment(img)
                    self.img_data.append(aug_img)
                    self.direction.append(int(direction_slice))

                img_data_arr = np.array(self.img_data)
                direction_data_arr = np.array(self.direction)

        x_train, x_valid, y_train, y_valid = model_selection.train_test_split(img_data_arr, direction_data_arr,
                                                                              random_state=7)
        # Create CNN model layers user Tensorflow framework
        model = Sequential(name="steering-model")

        model.add(Conv2D(24, (5, 5), activation="elu", strides=(2, 2), input_shape=(66, 200, 3)))
        model.add(Conv2D(36, (5, 5), activation="elu", strides=(2, 2)))
        model.add(Conv2D(48, (5, 5), activation="elu", strides=(2, 2)))
        model.add(Conv2D(64, (3, 3), activation="elu"))
        model.add(Dropout(0.5))
        model.add(Conv2D(64, (3, 3), activation="elu"))
        model.add(Flatten())
        model.add(Dropout(0.5))
        model.add(Dense(100, activation='elu'))
        model.add(Dense(50, activation='elu'))
        model.add(Dense(10, activation='elu'))
        model.add(Dense(1, activation='elu'))
        model.summary()

        print('training model...')
        train_model(model, x_train, x_valid, y_train, y_valid)
        print('saving model...')
        model.save('drive_model.h5')

# compile and train the model
def train_model(model, img_train, img_valid, direction_train, direction_valid):
    check = ModelCheckpoint('./checkpoints')
    model.compile(loss='mean_squared_error', optimizer=Adam(learning_rate=0.001))
    model.fit(img_train, direction_train, epochs=10, callbacks=[check], validation_data=(img_valid, direction_valid),
              shuffle=1, validation_steps=200)

# manipulate image data to give more instances of training data for the model to use
def img_augment(img):
    kernel = random.randint(1, 5)

    blur = cv2.blur(img, (kernel, kernel))

    return blur
