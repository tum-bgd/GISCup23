import cv2
import numpy as np


def GetHSV(r, g, b):
    print(cv2.cvtColor(np.uint8([[[r, g, b]]]), cv2.COLOR_RGB2HSV))


GetHSV(  0,   0, 255)  # blue
GetHSV(103, 168, 152)  # 06-03_2 has a green lake...
GetHSV(169,	206, 226)
GetHSV(182, 207, 220)