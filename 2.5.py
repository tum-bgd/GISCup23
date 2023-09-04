import cv2
import geopandas
import os
import rasterio.mask
import shapely

from matplotlib import pyplot as plt

from _config import *
from utils.dir import ReloadDir


def GetTileTopLeft(w, h):
    tileW = [STEP*i for i in range((w-TILE_W) // STEP + 1)]
    if tileW[-1] + TILE_W != w:
        tileW.append(w-TILE_W)
    tileH = [STEP*i for i in range((h-TILE_H) // STEP + 1)]
    if tileH[-1] + TILE_H != h:
        tileH.append(h-TILE_H)
    return tileW, tileH


def GetTilePlgn(picHandler, w, h):
    # xy()
    tl = picHandler.xy(h,          w,        )
    tr = picHandler.xy(h,          w+TILE_W-1)
    bl = picHandler.xy(h+TILE_H-1, w         )
    br = picHandler.xy(h+TILE_H-1, w+TILE_W-1)
    return shapely.Polygon((tl, tr, br, bl, tl))


def GetMaybeLakeMask(img):
    cv2HSVimg = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    return cv2.inRange(cv2HSVimg, LOWER_BLUE, UPPER_BLUE)/255


ReloadDir(PATH_OUT_TILE_MAYBE)
ReloadDir(PATH_OUT_TILE_MAYNO)
for fileName in os.listdir(PATH_REGN):
    if 'te' in fileName:
        print(fileName)
        with rasterio.open(PATH_REGN + fileName, "r") as pic:
            tileW, tileH = GetTileTopLeft(pic.width, pic.height)
            for w in tileW:
                for h in tileH:
                    tileBound = GetTilePlgn(pic, w, h)
                    out_image, _ = rasterio.mask.mask(pic, geopandas.GeoSeries([tileBound]), crop=True)
                    out_image = out_image.transpose(1, 2, 0)
                    assert out_image.shape == (TILE_H, TILE_W, 3)

                    outName = fileName[:-5] + '_' + str(w) + '_' + str(h) + '.jpg'
                    # skip images with too many black pixels (>=50%)
                    if numpy.sum(out_image == 0) >= 1024 * 1024 * 3 * 0.5:
                        plt.imsave(PATH_OUT_TILE_MAYNO + outName, out_image)
                        continue
                    # skip images with too small blue areas (<0.08%)
                    lakeRatio = numpy.sum(GetMaybeLakeMask(out_image) == 1) / 1024 / 1024
                    if lakeRatio < 0.0001:
                        plt.imsave(PATH_OUT_TILE_MAYNO + outName, out_image)
                        continue
                    plt.imsave(PATH_OUT_TILE_MAYBE + outName, out_image)
