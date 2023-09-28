import numpy

from torchvision.transforms import ToTensor
from torchvision.datasets import ImageFolder

from _config import *

# This script is used to get mean and std of all the training data.
# To run you need to move imgs to a subfolder

imgMean = [0, 0, 0]
imgStd  = [0, 0, 0]

dataset = ImageFolder(PATH_TR, transform=ToTensor())
for img, a in dataset:
    for i in range(3):
        imgMean[i] += img[i, :, :].mean()
        imgStd[i]  += img[i, :, :].std()
print(numpy.array(imgMean)/len(dataset), numpy.array(imgStd)/len(dataset))



# Results are:
# mean: [0.77585715 0.8034677  0.8158493 ] std: [0.11537416, 0.10468962, 0.10207428]
# mean has to be multiplied by 255 as defined by Detectron: [197.84357325, 204.8842635, 208.0415715]
# These values are already embedded in the config.

