import os
import shutil


def ReloadDir(path, gitkeep=False):
    try:
        shutil.rmtree(path)
    except Exception:
        pass
    finally:
        os.mkdir(path)
    if gitkeep:
        with open(path + '.gitkeep', mode='w', encoding="utf-8") as f:
            f.write('')
