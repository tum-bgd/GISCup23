import os
import pickle
import shutil


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
