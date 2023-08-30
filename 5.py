import json
import os
import pickle
import random
import shutil

from _config import *
from utils.dir import ReloadDir


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
    print("## Processing ##", tileFileName)
    thisDict = json.load(open(PATH_TILE_RECORD + tileFileName.replace('png', 'json'), 'r'))
    if i in trIdx:
        shutil.copy(PATH_TILE_WITHLABEL + tileFileName, PATH_TR + tileFileName)
        thisDict["file_name"] = PATH_TR + thisDict["file_name"]
        trDict.append(thisDict)
    elif i in vaIdx:
        shutil.copy(PATH_TILE_WITHLABEL + tileFileName, PATH_VA + tileFileName)
        thisDict["file_name"] = PATH_VA + thisDict["file_name"]
        vaDict.append(thisDict)
    i += 1

for d in trDict:
    assert(isinstance(d, dict))
for d in vaDict:
    assert(isinstance(d, dict))

pickle.dump(trDict, open(PATH_TR_DICT, 'wb'))
pickle.dump(vaDict, open(PATH_VA_DICT, 'wb'))
