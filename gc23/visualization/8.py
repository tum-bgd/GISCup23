# va plot
import cv2
import json
import numpy
import os
import pickle

from matplotlib import pyplot as plt
from PIL import Image

from gc23.utils.Dir import LoadPKL
from gc23.utils.Geometry import MaskToPlgn
from _config import *


for fileName in os.listdir('./output_va/est/'):
    regn = fileName[:7]
    tileW, tileH = list(map(int, fileName[:-4].split('_')[-2:]))
    masks, scores = LoadPKL('./output_va/est/' + fileName)
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

