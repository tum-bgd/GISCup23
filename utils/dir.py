import os
import shutil


def ReloadDir(path, gitkeep=False):
    shutil.rmtree(path)
    os.mkdir(path)
    if gitkeep:
        with open(path + '.gitkeep', mode='w', encoding="utf-8") as f:
            f.write('')
