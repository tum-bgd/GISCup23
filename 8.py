# for va
import cv2
import json
import numpy
import os
import pickle

from matplotlib import pyplot as plt
from PIL import Image
# from skimage import measure

from _config import *



def LoadEstimationFromPKL(pklPath):
    with open(pklPath, 'rb') as pklReader:
        return pickle.load(pklReader)


# def CloseContour(contour):
#     if not numpy.array_equal(contour[0], contour[-1]):
#         contour = numpy.vstack((contour, contour[0]))
#     return contour


# def MaskToPlgn(binary_mask, tolerance=0):
#     plgns = []
#     padded_binary_mask = numpy.pad(binary_mask, pad_width=1, mode='constant', constant_values=0)
#     contours = measure.find_contours(padded_binary_mask, 0.5)
#     print(len(contours)
#     contours = numpy.subtract(contours, 1)
#     for contour in contours:
#         contour = CloseContour(contour)
#         contour = measure.approximate_polygon(contour, tolerance)
#         if len(contour) < 3:
#             continue
#         contour = numpy.flip(contour, axis=1)
#         segmentation = contour.ravel().tolist()
#         # after padding and subtracting 1 we may get -0.5 points in our segmentation 
#         segmentation = [0 if i < 0 else i for i in segmentation]
#         plgns.append(segmentation)
#     return plgns


def MaskToPlgn(mask):
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    plgns = []
    for contour in contours:
        xs = []
        ys = []
        for point in contour:
            xs.append(int(point[0][0]))
            ys.append(int(point[0][1]))
        plgns.append([xs, ys])
    return plgns



for fileName in os.listdir('./output_va/est/'):
    regn = fileName[:7]
    tileW, tileH = list(map(int, fileName[:-4].split('_')[-2:]))
    masks, scores = LoadEstimationFromPKL('./output_va/est/' + fileName)
    masks = masks.astype(numpy.uint8)*255
    
    plt.figure(figsize=(16, 5), dpi=300.0)
    plt.subplot(131)
    plt.imshow(numpy.asarray(Image.open(PATH_TILE_WITHLABEL + fileName.replace('pkl', 'jpg'))))
    plt.subplot(132)
    plt.imshow(numpy.asarray(Image.open(PATH_TILE_WITHLABEL + fileName.replace('pkl', 'jpg'))))
    for mask in masks:
        plgns = MaskToPlgn(mask)  # only one actually
        for xs, ys in plgns:
            plt.plot(xs, ys, 'b')
    plt.subplot(133)
    plt.imshow(numpy.asarray(Image.open(PATH_TILE_WITHLABEL + fileName.replace('pkl', 'jpg'))))
    tileAnnos = json.load(open(PATH_TILE_RECORD + fileName.replace('pkl', 'json'), 'r'))["annotations"]
    for tileAnno in tileAnnos:
        anno = tileAnno["segmentation"][0]
        xs = anno[0::2]
        ys = anno[1::2]
        plt.plot(xs, ys, 'r')
    plt.savefig('./output_va/estplot/' + fileName.replace('pkl', 'jpg'), dpi='figure')
    plt.close()

