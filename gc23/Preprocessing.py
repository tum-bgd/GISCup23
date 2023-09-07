import copy
import geopandas
import pandas as pd
import rasterio.mask

from matplotlib import pyplot as plt

from . import *
from gc23.utils.File import ReloadDir
from gc23.utils.Geometry import *



def TrOrTE(date, reg):
    if date == '06-03' or date == '07-31':
        if int(reg) % 2 == 0:
            return 'tr'
    else:
        if int(reg) % 2 == 1:
            return 'tr'
    return 'te'


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


def SplitByRegn(reloadDir=True):
    reg = geopandas.read_file(PATH_RAW_REGION)
    REGION1 = {'name': '1', 'shape': reg[reg.region_num==1]["geometry"]}
    REGION2 = {'name': '2', 'shape': reg[reg.region_num==2]["geometry"]}
    REGION3 = {'name': '3', 'shape': reg[reg.region_num==3]["geometry"]}
    REGION4 = {'name': '4', 'shape': reg[reg.region_num==4]["geometry"]}
    REGION5 = {'name': '5', 'shape': reg[reg.region_num==5]["geometry"]}
    REGION6 = {'name': '6', 'shape': reg[reg.region_num==6]["geometry"]}
    ALL_REGION = [REGION1, REGION2, REGION3, REGION4, REGION5, REGION6]
    ALL_RAW_IMAGE = [RAW_IMAGE1, RAW_IMAGE2, RAW_IMAGE3, RAW_IMAGE4]
    if reloadDir:
        ReloadDir(PATH_PLGN)
        ReloadDir(PATH_REGN)
    mask = geopandas.read_file(PATH_RAW_TRAIN)
    for img in ALL_RAW_IMAGE:
        imgName = img.split('_')[3][5:]
        with rasterio.open(os.path.join(PATH_RAW, img), "r") as a:
            for r in ALL_REGION:
                # trX, teX
                maskedImgName = os.path.join(PATH_REGN, imgName + '_' + r['name'] + '_' + TrOrTE(imgName, r['name']) + '.tiff')
                out_image, out_transform = rasterio.mask.mask(a, r['shape'], crop=True)
                out_meta = a.meta
                out_meta.update({
                    "driver": "GTiff",
                    "height": out_image.shape[1],
                    "width": out_image.shape[2],
                    "transform": out_transform})
                with rasterio.open(maskedImgName, "w", **out_meta) as dest:
                    print('Writing', maskedImgName)
                    dest.write(out_image)
                # trY
                tar = mask[mask.image==img][mask.region_num==int(r['name'])]
                if len(tar):
                    maskedPLGName = os.path.join(PATH_PLGN, imgName + '_' + r['name'] + '.gpkg')
                    tar.to_file(maskedPLGName, driver="GPKG")


def CutTrRegnToTiles(reloadDir=True, plotTile=False):
    i = 0
    if reloadDir:
        ReloadDir(PATH_TMP_TR_TILE_MASK)
        ReloadDir(PATH_TMP_TR_TILE_PLGN)
        ReloadDir(PATH_TMP_TR_TILE_WITHLABEL)
        ReloadDir(PATH_TMP_TR_TILE_NONELABEL)
    for file in os.listdir(PATH_PLGN):
        plgn = geopandas.read_file(os.path.join(PATH_PLGN, file))
        sampledTile = geopandas.GeoDataFrame(columns=['tile'], crs="EPSG:3857", geometry='tile')
        regnName = os.path.join(PATH_REGN, file.replace('.gpkg', '_tr.tiff'))
        # print('## Processing', file)
        with rasterio.open(regnName, "r") as pic:
            # shape: HW
            picW, picH = pic.width, pic.height
            tileW, tileH = GetTileTopLeft(picW, picH)
            for w in tileW:
                for h in tileH:
                    tileBound = GetTilePlgn(pic, w, h)
                    out_image, _ = rasterio.mask.mask(pic, geopandas.GeoSeries([tileBound]), crop=True)
                    out_image = out_image.transpose(1, 2, 0)
                    assert out_image.shape == (TILE_H, TILE_W, 3)

                    # skip images with too many black pixels (>=50%)
                    if numpy.sum(out_image == 0) >= TILE_H * TILE_W * 3 * BLANK_RARIO:
                        # print('DROP:', regnName, w, h, "too many black pixels (>= 50%)")
                        continue

                    # skip images with too small blue areas (<0.01%)
                    lakeRatio = numpy.sum(GetMaybeLakeMask(out_image) == 1) / TILE_H / TILE_W
                    if lakeRatio < MAYBE_LAKE_RARIO:
                        # at least 0.01% pixels are likely to be a lake (approx. 105 pixels).
                        # print('DROP:', regnName, w, h, "too small blue areas {:.3f}% < 0.1%)".format(lakeRatio))
                        if lakeRatio != 0 and plotTile:
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
                        plt.imsave(os.path.join(PATH_TMP_TR_TILE_WITHLABEL, file[:-5] + '_' + str(w) + '_' + str(h) + '.jpg'), out_image)
                        # save label
                        plgnInTile.to_file(os.path.join(PATH_TMP_TR_TILE_PLGN, file[:-5] + '_' + str(w) + '_' + str(h) + '.gpkg'), driver="GPKG")
                        # update tile boundaries for this region
                        sampledTile = pd.concat([sampledTile, geopandas.GeoDataFrame({'tile': [GetTilePlgn(pic, w, h)]}, crs="EPSG:3857", geometry='tile')], ignore_index=True)
                        i += 1
                    else:
                        # without labels
                        plt.imsave(os.path.join(PATH_TMP_TR_TILE_NONELABEL, file[:-5] + '_' + str(w) + '_' + str(h) + '.jpg'), out_image)

        # check if all label are in tiles by union
        assert(isPlgnInTile(plgn, sampledTile).all())
        sampledTile.to_file(os.path.join(PATH_TMP_TR_TILE_MASK, file), driver="GPKG")
    print('# of img with labels in training areas:', i)


def CutTeRegnToTiles(reloadDir=True):
    i, j = 0, 0
    if reloadDir:
        ReloadDir(PATH_TMP_TE_TILE_MAYBE)
        ReloadDir(PATH_TMP_TE_TILE_MAYNO)
    for fileName in os.listdir(PATH_REGN):
        if 'te' in fileName:
            with rasterio.open(os.path.join(PATH_REGN, fileName), "r") as pic:
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
                            plt.imsave(os.path.join(PATH_TMP_TE_TILE_MAYNO, outName), out_image)
                            j += 1
                            continue

                        # skip images with too small blue areas (<0.01%)
                        lakeRatio = numpy.sum(GetMaybeLakeMask(out_image) == 1) / 1024 / 1024
                        if lakeRatio < MAYBE_LAKE_RARIO:
                            plt.imsave(os.path.join(PATH_TMP_TE_TILE_MAYNO, outName), out_image)
                            j += 1
                            continue

                        plt.imsave(os.path.join(PATH_TMP_TE_TILE_MAYBE, outName), out_image)
                        i += 1
    print('# of img probably with labels in testing areas:', i)
    print('# of img unlikely with labels in testing areas:', j)


def GetRegnSize(regnPath):
     with rasterio.open(regnPath, "r") as pic:
        return pic.height, pic.width
