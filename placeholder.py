import numpy as np
import cv2 as cv
from time import sleep, time
import sys
from math import sqrt
# import random
import os
from pyghthouse import Pyghthouse
#from alph import *
from config import UNAME, TOKEN

class ImageReturner:
    def __init__(self, cap, subtitles={0:None}):
        self.cap = cap
        self.subtitles = subtitles
        self.count = 1
        self.num_fr = int(cap.get(7))

    def callback(self, events):
        try:
            ret, frame = self.cap.read()

            width, height = frame.shape[1], frame.shape[0]
            if width>height:
                frame = frame[:,int((width-height)/2):-int((width-height)/2)]
            else:
                frame = frame[int((height-width)/2):-int((height-width)/2),:]

            frame = cv.resize(frame, (28,14))
            img = frame[...,::-1].tolist()

            self.count += 1
            return img
        except:
            Pyghthouse.stop(p)

cap = cv.VideoCapture("ricky.mp4")

fr = int(cap.get(5))

i = ImageReturner(cap)

p = Pyghthouse(UNAME, TOKEN, image_callback=i.callback, frame_rate=fr)
Pyghthouse.start(p)

while True:
    print(i.count)
    if i.count >= i.num_fr:
        Pyghthouse.stop(p)
        break
    sleep(0.1)
