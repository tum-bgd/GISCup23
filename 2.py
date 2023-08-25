import cv2
import os
import pandas as pd
import shapely
import rasterio.mask

from matplotlib import pyplot as plt

from _config import *
from utils.dir import ReloadDir


# maxH = 0
# maxW = 0
# for file in os.listdir(PATH_PLGN):
#     if '.gpkg' in file:
#         plgns = geopandas.read_file(PATH_PLGN + file)
#         with rasterio.open(PATH_REGN + file.replace('.gpkg', '_tr.tiff'), "r") as pic:
#             for plgn in plgns['geometry']:
#                 hhh = geopandas.GeoSeries([plgn])
#                 out_image, _ = rasterio.mask.mask(pic, hhh, crop=True)
#                 _, thisH, thisW = out_image.shape
#                 if thisH > maxH:
#                     maxH = thisH
#                 if thisW > maxW:
#                     maxW = thisW
# print(maxH, maxW)

# we know that the max H and W for ice lakes are 790 and 1134.


# def coord2loc(picHandler, coord):
#     assert 0 <= coord[0] and coord[0] <= picHandler.width
#     assert 0 <= coord[1] and coord[1] <= picHandler.height
#     return picHandler.transform * (coord[0], coord[1])

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
    return [shapely.Polygon((tl, tr, br, bl, tl))]


def GetMaybeLakeMask(img):
    cv2HSVimg = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    return cv2.inRange(cv2HSVimg, LOWER_BLUE, UPPER_BLUE)/255


i = 0
PLOT_TILE_MASK = False
ReloadDir(PATH_TILEMASK, gitkeep=True)
for file in os.listdir(PATH_PLGN):
    if '.gpkg' in file:
        plgns = geopandas.read_file(PATH_PLGN + file)
        sampledTile = geopandas.GeoDataFrame(columns=['tile'], crs="EPSG:3857", geometry='tile')
        regnName = PATH_REGN + file.replace('.gpkg', '_tr.tiff')
        with rasterio.open(regnName, "r") as pic:
            # shape: HW
            picW, picH = pic.width, pic.height
            tileW, tileH = GetTileTopLeft(picW, picH)
            for w in tileW:
                for h in tileH:
                    out_image, _ = rasterio.mask.mask(pic, geopandas.GeoSeries(GetTilePlgn(pic, w, h)), crop=True)
                    out_image = out_image.transpose(1, 2, 0)
                    assert out_image.shape == (1024, 1024, 3)

                    # skip images with too many black pixels (>=50%)
                    if numpy.sum(out_image == 0) >= 1024 * 1024 * 3 * 0.5:
                        # print('DROP:', regnName, w, h, "too many black pixels (>= 50%)")
                        continue

                    # skip images with too small blue areas (<0.08%)
                    lakeRatio = numpy.sum(GetMaybeLakeMask(out_image) == 1) / 1024 / 1024
                    if lakeRatio < 0.001:
                        print('DROP:', regnName, w, h, "too small blue areas {:.3f}% < 0.1%)".format(lakeRatio))
                        if lakeRatio != 0 and PLOT_TILE_MASK:
                            plt.subplot(121)
                            plt.imshow(out_image)
                            plt.subplot(122)
                            plt.imshow(GetMaybeLakeMask(out_image)==1)
                            plt.show()
                        continue

                    # check whether have label

                    # check if all label are in tiles. If not, add them.

                    # update tile boundaries for this region
                    sampledTile = pd.concat([sampledTile, geopandas.GeoDataFrame({'tile': GetTilePlgn(pic, w, h)}, crs="EPSG:3857", geometry='tile')], ignore_index=True)
                    i += 1

        sampledTile.to_file(PATH_TILEMASK + file, driver="GPKG")
print(i)



                    # print(w, h)
            # print(pic.bounds)
            # print(pic.width, pic.height)
            # print(len(tileW) * len(tileH))
            # print(pic.transform)
            # print(pic.transform * (0, 0), pic.xy(0, 0))
            # print(pic.index(pic.bounds.left, pic.bounds.top))
