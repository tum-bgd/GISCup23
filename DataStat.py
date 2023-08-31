import numpy

from torchvision.transforms import ToTensor
from torchvision.datasets import ImageFolder

from _config import *


imgMean = [0, 0, 0]
imgStd  = [0, 0, 0]

dataset = ImageFolder(PATH_TR, tranform=ToTensor())
for img, a in dataset:
    for i in range(3):
        imgMean[i] += img[i, :, :].mean()
        imgStd[i]  += img[i, :, :].std()
print(numpy.array(imgMean)/len(dataset), numpy.array(imgStd)/len(dataset))
