import json
import geopandas
import pickle
import random
import rasterio
import shapely
import shutil

from matplotlib import pyplot as plt
from PIL import Image

from . import *
from gc23.utils.Dir import ReloadDir


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


def PrepareTileLabel(reloadDir=True, plotTile=False):
    # get json label formatted for detectron2
    # TODO why plus 0.5, although float required, then why not add 0.1
    if reloadDir:
        ReloadDir(PATH_TMP_TR_TILE_JSON)
    k = 0
    for tileFileName in os.listdir(PATH_TMP_TR_TILE_WITHLABEL):
        record = {}
        record["file_name"] = tileFileName
        record["image_id"] = k
        record["height"] = TILE_H
        record["width"] = TILE_W

        a = tileFileName[:-4].split('_')
        w = int(a[2])
        h = int(a[3])

        rawTilePlgn = geopandas.read_file(os.path.join(PATH_TMP_TR_TILE_PLGN, tileFileName.replace('jpg', 'gpkg')))
        tilePlgn = GetPlgnList(rawTilePlgn)
        with rasterio.open(os.path.join(PATH_REGN, a[0] + '_' + a[1] + '_tr.tiff'), "r") as regn:
            allPlgn = []
            plt.figure()
            plt.subplot(121)
            plt.imshow(numpy.asarray(Image.open(os.path.join(PATH_TMP_TR_TILE_WITHLABEL, tileFileName))))
            plt.subplot(122)
            plt.imshow(numpy.asarray(Image.open(os.path.join(PATH_TMP_TR_TILE_WITHLABEL, tileFileName))))
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
            if plotTile:
                plt.show()
            record["annotations"] = allPlgn
            plt.close()
        k += 1
        with open(os.path.join(PATH_TMP_TR_TILE_JSON, tileFileName.replace('jpg', 'json')), "w") as jsonFile:
            json.dump(record, jsonFile)


def TrVASplit(trRatio, reloadDir=True):
    if reloadDir:
        ReloadDir(PATH_TMP_TR_TRAIN)
        ReloadDir(PATH_TMP_TR_VALID)

    nImg = len(os.listdir(PATH_TMP_TR_TILE_WITHLABEL))
    allIdx = list(range(nImg))
    trIdx = random.sample(allIdx, int(trRatio*nImg))
    vaIdx = [idx for idx in allIdx if idx not in trIdx]

    i = 0
    trDict = []
    vaDict = []
    for tileFileName in os.listdir(PATH_TMP_TR_TILE_WITHLABEL):
        thisDict = json.load(open(os.path.join(PATH_TMP_TR_TILE_JSON, tileFileName.replace('jpg', 'json')), 'r'))
        if i in trIdx:
            shutil.copy(
                os.path.join(PATH_TMP_TR_TILE_WITHLABEL, tileFileName),
                os.path.join(PATH_TMP_TR_TRAIN, tileFileName))
            thisDict["file_name"] = os.path.join(PATH_TMP_TR_TRAIN, thisDict["file_name"])
            trDict.append(thisDict)
        elif i in vaIdx:
            shutil.copy(
                os.path.join(PATH_TMP_TR_TILE_WITHLABEL, tileFileName),
                os.path.join(PATH_TMP_TR_VALID, tileFileName))
            thisDict["file_name"] = os.path.join(PATH_TMP_TR_VALID, thisDict["file_name"])
            vaDict.append(thisDict)
        i += 1

    for d in trDict:
        assert(isinstance(d, dict))
    for d in vaDict:
        assert(isinstance(d, dict))

    pickle.dump(trDict, open(PATH_TMP_TR_TR_DICT, 'wb'))
    pickle.dump(vaDict, open(PATH_TMP_TR_VA_DICT, 'wb'))
