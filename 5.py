import json
import os
import pickle
import random
import shutil

from _config import *
from model import PATH_TR_DICT, PATH_VA_DICT
from utils.dir import ReloadDir


def GetEmptyDict(idx):
    return {
        "image_id":     idx,
        "height":       TILE_H,
        "width":        TILE_W,
        "annotations":  [{
            "bbox": [],
            "bbox_mode": 0,  # BoxMode.XYXY_ABS
            "segmentation": [],
            "category_id": 0,
        }]
    }


RELOAD = True
if RELOAD:
    ReloadDir(PATH_TR)
    ReloadDir(PATH_VA)

nImg = len(os.listdir(PATH_TILE_WITHLABEL))
allIdx = list(range(nImg))
trIdx = random.sample(allIdx, int(TR_RATIO*nImg))
vaIdx = [idx for idx in allIdx if idx not in trIdx]

i = 0
trDict = []
vaDict = []
for tileFileName in os.listdir(PATH_TILE_WITHLABEL):
    thisDict = json.load(open(PATH_TILE_RECORD + tileFileName.replace('jpg', 'json'), 'r'))
    if i in trIdx:
        shutil.copy(PATH_TILE_WITHLABEL + tileFileName, PATH_TR + tileFileName)
        thisDict["file_name"] = PATH_TR + thisDict["file_name"]
        trDict.append(thisDict)
    elif i in vaIdx:
        shutil.copy(PATH_TILE_WITHLABEL + tileFileName, PATH_VA + tileFileName)
        thisDict["file_name"] = PATH_VA + thisDict["file_name"]
        vaDict.append(thisDict)
    i += 1

# add 500 imgs without plgn
selectedIdx = random.sample(list(range(len(os.listdir(PATH_TILE_NONELABEL)))), 500)
trIdx = random.sample(selectedIdx, int(len(selectedIdx)))
vaIdx = [idx for idx in selectedIdx if idx not in trIdx]
k = 0
for tileFileName in os.listdir(PATH_TILE_NONELABEL):
    if k in trIdx:
        shutil.copy(PATH_TILE_NONELABEL + tileFileName, PATH_TR + tileFileName)
        thisDict = GetEmptyDict(k+nImg)
        thisDict["file_name"] = PATH_TR + tileFileName
        trDict.append(thisDict)
    elif k in vaIdx:
        shutil.copy(PATH_TILE_NONELABEL + tileFileName, PATH_VA + tileFileName)
        thisDict = GetEmptyDict(k+nImg)
        thisDict["file_name"] = PATH_VA + tileFileName
        vaDict.append(thisDict)
    k += 1

for d in trDict:
    assert(isinstance(d, dict))
for d in vaDict:
    assert(isinstance(d, dict))

pickle.dump(trDict, open(PATH_TR_DICT, 'wb'))
pickle.dump(vaDict, open(PATH_VA_DICT, 'wb'))
