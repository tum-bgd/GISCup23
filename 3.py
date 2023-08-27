import json
import numpy
import os
import rasterio

# from detectron2.structures import BoxMode
from matplotlib import pyplot as plt
from PIL import Image

from _config import *
from utils.dir import ReloadDir


# TODO argparse
# TODO fix multi-polygon https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.explode.html
# TODO why plus 0.5
PLOT = False
RELOAD = True
if RELOAD:
    ReloadDir(PATH_TILE_RECORD, gitkeep=True)

k = 0
for tileFileName in os.listdir(PATH_TILE_WITHLABEL):
    if '.png' in tileFileName:
        print("## Processing", k, "##", tileFileName)

        record = {}
        record["file_name"] = tileFileName
        record["image_id"] = k
        record["height"] = TILE_H
        record["width"] = TILE_W

        a = tileFileName[:-4].split('_')
        w = int(a[2])
        h = int(a[3])

        tilePlgn = geopandas.read_file(PATH_TILE_PLGN + tileFileName.replace('png', 'gpkg'))
        with rasterio.open(PATH_REGN + a[0] + '_' + a[1] + '_tr.tiff', "r") as regn:
            allPlgn = []
            plt.subplot(121)
            plt.imshow(numpy.asarray(Image.open(PATH_TILE_WITHLABEL + tileFileName)))
            plt.subplot(122)
            plt.imshow(numpy.asarray(Image.open(PATH_TILE_WITHLABEL + tileFileName)))
            for i in range(len(tilePlgn)):
                plgn = tilePlgn.iloc[i].values[0].exterior.coords
                allX, allY = [], []
                for point in plgn:
                    y, x = regn.index(point[0], point[1])
                    allX.append(x-w)
                    allY.append(y-h)
                # I truly do not know why plus 0.5. I just mimic the steps in the balloon example of detectron2
                thisSegm = [(x + 0.5, y + 0.5) for x, y in zip(allX, allY)]
                thisSegm = [p for x in thisSegm for p in x]
                thisAnno = {
                    "bbox": [min(allX), min(allY), max(allX), max(allY)],
                    "bbox_mode": 0,  # BoxMode.XYXY_ABS
                    "segmentation": [thisSegm],
                    "category_id": 0,
                }
                allPlgn.append(thisAnno)
                plt.plot(allX, allY, 'r')
            if PLOT or tileFileName == "06-03_2_3584_1024.png":
                plt.show()
            record["annotations"] = allPlgn
        k += 1
        with open(PATH_TILE_RECORD + tileFileName.replace('png', 'json'), "w") as jsonFile:
            json.dump(record, jsonFile)
