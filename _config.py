import geopandas
import numpy


PATH_RAW = "./raw/"
PATH_RAW_TRAIN = PATH_RAW + "lake_polygons_training.gpkg"
PATH_RAW_REGION = PATH_RAW + "lakes_regions.gpkg"

PATH_PLGN = "./data/plgn/"
PATH_REGN = "./data/regn/"
PATH_TILE_MASK = "./data/tilemask/"
PATH_TILE_PLGN = "./data/tileplgn/"
PATH_TILE_WITHLABEL = "./data/tilewithlabel/"
PATH_TILE_NONELABEL = "./data/tilenonelabel/"


RAW_IMAGE1 = "Greenland26X_22W_Sentinel2_2019-06-03_05.tif"
RAW_IMAGE2 = "Greenland26X_22W_Sentinel2_2019-06-19_20.tif"
RAW_IMAGE3 = "Greenland26X_22W_Sentinel2_2019-07-31_25.tif"
RAW_IMAGE4 = "Greenland26X_22W_Sentinel2_2019-08-25_29.tif"

ALL_RAW_IMAGE = [RAW_IMAGE1, RAW_IMAGE2, RAW_IMAGE3, RAW_IMAGE4]

reg = geopandas.read_file(PATH_RAW_REGION)

REGION1 = {'name': '1', 'shape': reg[reg.region_num==1]["geometry"]}
REGION2 = {'name': '2', 'shape': reg[reg.region_num==2]["geometry"]}
REGION3 = {'name': '3', 'shape': reg[reg.region_num==3]["geometry"]}
REGION4 = {'name': '4', 'shape': reg[reg.region_num==4]["geometry"]}
REGION5 = {'name': '5', 'shape': reg[reg.region_num==5]["geometry"]}
REGION6 = {'name': '6', 'shape': reg[reg.region_num==6]["geometry"]}

ALL_REGION = [REGION1, REGION2, REGION3, REGION4, REGION5, REGION6]

TILE_H = 1024
TILE_W = 1024
STEP = 512

LOWER_BLUE = numpy.array([ 80,  35,  35])
UPPER_BLUE = numpy.array([130, 255, 255])


def TrOrTE(date, reg):
    if date == '06-03' or date == '07-31':
        if int(reg) % 2 == 0:
            return 'tr'
    else:
        if int(reg) % 2 == 1:
            return 'tr'
    return 'te'
