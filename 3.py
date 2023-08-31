import json
import geopandas
import os
import rasterio
import shapely

# from detectron2.structures import BoxMode
from matplotlib import pyplot as plt
from PIL import Image

from _config import *
from utils.dir import ReloadDir


# TODO argparse
# TODO why plus 0.5
PLOT = False
RELOAD = True
if RELOAD:
    ReloadDir(PATH_TILE_RECORD)


def GetPlgnList(plgn):
    res = []
    for i in range(len(plgn)):
        thisPlgn = plgn.geometry.iloc[i]
        if isinstance(thisPlgn, shapely.Polygon):
            # this is a plgn, to res
            res.append(thisPlgn)
        elif isinstance(thisPlgn, shapely.MultiPolygon):
            # this is a multiplgn, transform into list of plgns, then append
            res += list(thisPlgn.geoms)
        else:
            raise Exception
    assert [isinstance(x, shapely.Polygon) for x in res]
    return res


k = 0
for tileFileName in os.listdir(PATH_TILE_WITHLABEL):
    print("## Processing", k, "##", tileFileName)

    record = {}
    record["file_name"] = tileFileName
    record["image_id"] = k
    record["height"] = TILE_H
    record["width"] = TILE_W

    a = tileFileName[:-4].split('_')
    w = int(a[2])
    h = int(a[3])

    rawTilePlgn = geopandas.read_file(PATH_TILE_PLGN + tileFileName.replace('jpg', 'gpkg'))
    tilePlgn = GetPlgnList(rawTilePlgn)
    with rasterio.open(PATH_REGN + a[0] + '_' + a[1] + '_tr.tiff', "r") as regn:
        allPlgn = []
        plt.figure()
        plt.subplot(121)
        plt.imshow(numpy.asarray(Image.open(PATH_TILE_WITHLABEL + tileFileName)))
        plt.subplot(122)
        plt.imshow(numpy.asarray(Image.open(PATH_TILE_WITHLABEL + tileFileName)))
        for i in range(len(tilePlgn)):
            plgn = tilePlgn[i].exterior.coords
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
        if PLOT:
            plt.show()
        record["annotations"] = allPlgn
        plt.close()
    k += 1
    with open(PATH_TILE_RECORD + tileFileName.replace('jpg', 'json'), "w") as jsonFile:
        json.dump(record, jsonFile)
