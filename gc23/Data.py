import geopandas
import pandas as pd
import random
import rasterio
import shapely
import shutil

from matplotlib import pyplot as plt

from . import *
from gc23.Preprocessing import GetRegnSize
from gc23.utils.File import LoadImg, LoadJson, LoadPKL, ReloadDir, SaveJson, SavePKL
from gc23.utils.Geometry import MaskToPlgn, PlgnToWorldPlgn


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
            plt.imshow(LoadImg(os.path.join(PATH_TMP_TR_TILE_WITHLABEL, tileFileName)))
            plt.subplot(122)
            plt.imshow(LoadImg(os.path.join(PATH_TMP_TR_TILE_WITHLABEL, tileFileName)))
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
        SaveJson(record, os.path.join(PATH_TMP_TR_TILE_JSON, tileFileName.replace('jpg', 'json')))


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
        thisDict = LoadJson(os.path.join(PATH_TMP_TR_TILE_JSON, tileFileName.replace('jpg', 'json')))
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

    SavePKL(trDict, PATH_TMP_TR_TR_DICT)
    SavePKL(vaDict, PATH_TMP_TR_VA_DICT)


def GetRegnEstMask(regnFileName, _plot=False):
    h, w = GetRegnSize(os.path.join(PATH_REGN, regnFileName))
    res = {
        'estim': numpy.zeros((h, w)),
        'count': numpy.zeros((h, w))
    }
    regnPrefix = regnFileName[:-5]

    for estmFileName in os.listdir(PATH_TMP_TE_ESTM):
        if regnPrefix in estmFileName:
            tlW, tlH = list(map(int, estmFileName[:-4].split('_')[-2:]))  # tl = topleft
            masks, score = LoadPKL(os.path.join(PATH_TMP_TE_ESTM, estmFileName))
            if masks.shape[0]:
                # have estimation (the predictor thinks there are lakes)
                masks = masks.astype(float)
                res['count'][tlH:tlH+TILE_H, tlW:tlW+TILE_W] += 1
                for i in range(masks.shape[0]):
                    res['estim'][tlH:tlH+TILE_H, tlW:tlW+TILE_W] += masks[i] * score[i]
    res['estim'][res['estim'] < res['count'] * CONFINDENCE] = 0
    res['estim'] = res['estim'] > 0
    # TODO: remove estimations at coast
    if _plot:
        plt.figure(figsize=(16.5, 8), dpi=600)
        plt.subplot(121)
        plt.imshow(res['estim'])
        plt.subplot(122)
        plt.imshow(res['count'])
        plt.savefig(os.path.join(PATH_TMP_TE_ESTM_REGN_PLOT, regnFileName.replace('tiff', 'jpg')), dpi='figure')
        plt.close()
    SavePKL(res['estim'], os.path.join(PATH_TMP_TE_ESTM_REGN, regnFileName.replace('tiff', 'pkl')))


def GetAllRegnEstMask(plot=False):
    ReloadDir(PATH_TMP_TE_ESTM_REGN)
    ReloadDir(PATH_TMP_TE_ESTM_REGN_PLOT)
    for regnFileName in os.listdir(PATH_REGN):
        if 'te' in regnFileName:
            GetRegnEstMask(regnFileName, _plot=plot)


def is_narrow_stream(polygon):
    # get minimum bounding rectangle
    box = shapely.minimum_rotated_rectangle(polygon)

    # get coordinates of polygon vertices
    x, y = box.exterior.coords.xy

    # get length of bounding box edges
    edge_length = (
        shapely.Point(x[0], y[0]).distance(shapely.Point(x[1], y[1])),
        shapely.Point(x[1], y[1]).distance(shapely.Point(x[2], y[2])))

    # get length and width of polygon as the longest and shortest edges of the rectangle
    length = max(edge_length)
    width = min(edge_length)

    return width/length < 0.1


def RegnMaskToWorldPlgn():
    ReloadDir(PATH_TMP_TE_ESTM_REAL_GPKG)
    for resFileName in os.listdir(PATH_TMP_TE_ESTM_REGN):
        date, regnIdx = resFileName.split('_')[:2]
        gdf = geopandas.GeoDataFrame(columns=['image', 'region_num', 'geometry'], crs="EPSG:3857", geometry='geometry')
        res = LoadPKL(os.path.join(PATH_TMP_TE_ESTM_REGN, resFileName))
        plgns = MaskToPlgn(res)
        with rasterio.open(os.path.join(PATH_REGN, resFileName.replace('pkl', 'tiff')), 'r') as regn:
            for plgn in plgns:
                wPlgn = PlgnToWorldPlgn(regn, plgn)
                if wPlgn:
                    if isinstance(shapely.minimum_rotated_rectangle(wPlgn), shapely.Polygon):
                        gdf = pd.concat([
                            gdf,
                            geopandas.GeoDataFrame({
                                     'image': [DATE2IMG[date]],
                                'region_num': [int(regnIdx)],
                                  'geometry': [wPlgn]}, crs="EPSG:3857", geometry='geometry')], ignore_index=True)

        # Remove the holes (inner polygons) from the generated polygons
        gdf["geometry"] = gdf["geometry"].apply(lambda row: shapely.Polygon(row.exterior) if row.interiors else row)
        # drop polygons that are narrow streams
        gdf.drop(gdf[gdf["geometry"].apply(is_narrow_stream)].index, inplace=True)
        # drop polygons that are smaller than 0.1km^2
        gdf.drop(gdf[gdf["geometry"].area < 100000].index, inplace=True)
        gdf.to_file(os.path.join(PATH_TMP_TE_ESTM_REAL_GPKG, resFileName.replace('_te.pkl', '.gpkg')), driver="GPKG")


def GetFinalResult():
    gdf = geopandas.GeoDataFrame(columns=['image', 'region_num', 'geometry'], crs="EPSG:3857", geometry='geometry')
    for fileName in sorted(os.listdir(PATH_TMP_TE_ESTM_REAL_GPKG)):
        plgn = geopandas.read_file(os.path.join(PATH_TMP_TE_ESTM_REAL_GPKG, fileName))
        gdf = pd.concat([gdf, plgn], ignore_index=True)
    gdf.to_file(PATH_FINAL, driver="GPKG")
