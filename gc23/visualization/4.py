import json
import os

from matplotlib import pyplot as plt
from PIL import Image

from gc23.utils.Dir import ReloadDir
from _config import *


RELOAD = True
if RELOAD:
    ReloadDir(PATH_TILE_PLOT)

for tileFileName in os.listdir(PATH_TILE_WITHLABEL):
    print("## Processing ##", tileFileName)
    plt.figure(figsize=(5.5, 5), dpi=200.0)
    plt.imshow(numpy.asarray(Image.open(PATH_TILE_WITHLABEL + tileFileName)))
    tileAnnos = json.load(open(PATH_TILE_RECORD + tileFileName.replace('jpg', 'json'), 'r'))["annotations"]
    for tileAnno in tileAnnos:
        anno = tileAnno["segmentation"][0]
        xs = anno[0::2]
        ys = anno[1::2]
        plt.plot(xs, ys, 'r')
    plt.savefig(PATH_TILE_PLOT + tileFileName, dpi='figure')
    plt.close()
