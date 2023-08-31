import copy
import cv2
import geopandas
import os
import pandas as pd
import shapely
import rasterio.mask

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


def GetIntersection(tile, plgnInRegn):
    plgn = plgnInRegn.intersection(tile)
    return plgn[~plgn.is_empty]


def isPlgnInTile(plgn, tile):
    res = numpy.empty((len(plgn), ), dtype=bool)
    aaa = copy.deepcopy(tile)
    aaa['dummy'] = 0
    union = aaa.dissolve(by='dummy')
    for k in range(len(plgn)):
        res[k] = plgn['geometry'].iloc[k].within(union).iloc[0].values[0]
    return res


i = 0
# TODO: switch to command line options
PLOT_TILE_MASK = False
RELOAD = True
if RELOAD:
    ReloadDir(PATH_TILE_MASK)
    ReloadDir(PATH_TILE_PLGN)
    ReloadDir(PATH_TILE_WITHLABEL)
    ReloadDir(PATH_TILE_NONELABEL)
for file in os.listdir(PATH_PLGN):
    plgn = geopandas.read_file(PATH_PLGN + file)
    sampledTile = geopandas.GeoDataFrame(columns=['tile'], crs="EPSG:3857", geometry='tile')
    regnName = PATH_REGN + file.replace('.gpkg', '_tr.tiff')
    print('## Processing', file)
    with rasterio.open(regnName, "r") as pic:
        # shape: HW
        picW, picH = pic.width, pic.height
        tileW, tileH = GetTileTopLeft(picW, picH)
        for w in tileW:
            for h in tileH:
                tileBound = GetTilePlgn(pic, w, h)
                out_image, _ = rasterio.mask.mask(pic, geopandas.GeoSeries([tileBound]), crop=True)
                out_image = out_image.transpose(1, 2, 0)
                assert out_image.shape == (1024, 1024, 3)

                # skip images with too many black pixels (>=50%)
                if numpy.sum(out_image == 0) >= 1024 * 1024 * 3 * 0.5:
                    # print('DROP:', regnName, w, h, "too many black pixels (>= 50%)")
                    continue

                # skip images with too small blue areas (<0.08%)
                lakeRatio = numpy.sum(GetMaybeLakeMask(out_image) == 1) / 1024 / 1024
                if lakeRatio < 0.0001:
                    # at least 0.01% pixels are likely to be a lake (approx. 105 pixels).
                    # print('DROP:', regnName, w, h, "too small blue areas {:.3f}% < 0.1%)".format(lakeRatio))
                    if lakeRatio != 0 and PLOT_TILE_MASK:
                        plt.subplot(121)
                        plt.imshow(out_image)
                        plt.subplot(122)
                        plt.imshow(GetMaybeLakeMask(out_image)==1)
                        plt.show()
                    continue

                # check whether have label
                plgnInTile = GetIntersection(tileBound, plgn)
                if len(plgnInTile):
                    # with labels
                    plt.imsave(PATH_TILE_WITHLABEL + file[:-5] + '_' + str(w) + '_' + str(h) + '.jpg', out_image)
                    # save label
                    plgnInTile.to_file(PATH_TILE_PLGN + file[:-5] + '_' + str(w) + '_' + str(h) + '.gpkg', driver="GPKG")
                    # update tile boundaries for this region
                    sampledTile = pd.concat([sampledTile, geopandas.GeoDataFrame({'tile': [GetTilePlgn(pic, w, h)]}, crs="EPSG:3857", geometry='tile')], ignore_index=True)
                    i += 1
                else:
                    # without labels
                    plt.imsave(PATH_TILE_NONELABEL + file[:-5] + '_' + str(w) + '_' + str(h) + '.jpg', out_image)

    # check if all label are in tiles by union
    assert(isPlgnInTile(plgn, sampledTile).all())
    sampledTile.to_file(PATH_TILE_MASK + file, driver="GPKG")

print('# of img with labels:', i)
