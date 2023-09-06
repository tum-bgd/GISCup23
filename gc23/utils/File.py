import json
import numpy
import os
import pickle
import shutil

from PIL import Image


def ReloadDir(path, gitkeep=False):
    try:
        shutil.rmtree(path)
    except Exception:
        pass
    finally:
        os.makedirs(path)
    if gitkeep:
        with open(path + '.gitkeep', mode='w', encoding="utf-8") as f:
            f.write('')


def LoadPKL(pklPath):
    with open(pklPath, 'rb') as pklReader:
        return pickle.load(pklReader)


def SavePKL(var, pklPath):
    with open(pklPath, 'wb') as pklWriter:
        pickle.dump(var, pklWriter)


def LoadImg(imgPath):
    return numpy.asarray(Image.open(imgPath))


def LoadJson(jsonPath):
    with open(jsonPath, 'r') as jsonReader:
        return json.load(jsonReader)


def SaveJson(var, jsonPath):
    with open(jsonPath, 'w') as jsonWriter:
        return json.dump(var, jsonWriter)


