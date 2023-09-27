import numpy
import os


# given info
RAW_IMAGE1 = "Greenland26X_22W_Sentinel2_2019-06-03_05.tif"
RAW_IMAGE2 = "Greenland26X_22W_Sentinel2_2019-06-19_20.tif"
RAW_IMAGE3 = "Greenland26X_22W_Sentinel2_2019-07-31_25.tif"
RAW_IMAGE4 = "Greenland26X_22W_Sentinel2_2019-08-25_29.tif"
DATE2IMG = {
    '06-03': RAW_IMAGE1,
    '06-19': RAW_IMAGE2,
    '07-31': RAW_IMAGE3,
    '08-25': RAW_IMAGE4
}
PATH_RAW = "../raw"
PATH_RAW_TRAIN =  os.path.join(PATH_RAW, "lake_polygons_training.gpkg")
PATH_RAW_REGION = os.path.join(PATH_RAW, "lakes_regions.gpkg")

# prepare path
PATH_TMP = "./tmp"
PATH_TMP_DATA = os.path.join(PATH_TMP, 'data')
PATH_TMP_TR = os.path.join(PATH_TMP, 'tr')
PATH_TMP_TE = os.path.join(PATH_TMP, 'te')

# for data
PATH_PLGN = os.path.join(PATH_TMP_DATA, "plgn")
PATH_REGN = os.path.join(PATH_TMP_DATA, "regn")

# for training
PATH_TMP_TR_TILE_MASK = os.path.join(PATH_TMP_TR, "tilemask")
PATH_TMP_TR_TILE_PLGN = os.path.join(PATH_TMP_TR, "tileplgn")
PATH_TMP_TR_TILE_PLOT = os.path.join(PATH_TMP_TR, "tileplot")
PATH_TMP_TR_TILE_JSON = os.path.join(PATH_TMP_TR, "tilejson")
PATH_TMP_TR_TILE_WITHLABEL = os.path.join(PATH_TMP_TR, "tilewithlabel")
PATH_TMP_TR_TILE_NONELABEL = os.path.join(PATH_TMP_TR, "tilenonelabel")
PATH_TMP_TR_TRAIN = os.path.join(PATH_TMP_TR, 'train')
PATH_TMP_TR_VALID = os.path.join(PATH_TMP_TR, 'valid')
PATH_TMP_TR_TR_DICT = os.path.join(PATH_TMP_TR, 'trDict.pkl')
PATH_TMP_TR_VA_DICT = os.path.join(PATH_TMP_TR, 'vaDict.pkl')
PATH_TMP_TR_VA_ESTM = os.path.join(PATH_TMP_TR, 'validest')
PATH_TMP_TR_VA_ESTM_PLOT = os.path.join(PATH_TMP_TR, 'validestplot')

PATH_MODEL_TR_OUTPUT = "./model/output"

# for testing
PATH_TMP_TE_TILE_MAYBE = os.path.join(PATH_TMP_TE, "tilemaybe")
PATH_TMP_TE_TILE_MAYNO = os.path.join(PATH_TMP_TE, "tilemayno")
PATH_TMP_TE_TILE_PLOT = os.path.join(PATH_TMP_TE, "tileplot")
PATH_TMP_TE_ESTM = os.path.join(PATH_TMP_TE, "estm")
PATH_TMP_TE_ESTM_PLOT = os.path.join(PATH_TMP_TE, "estmplot")
PATH_TMP_TE_ESTM_REGN = os.path.join(PATH_TMP_TE, "estmregn")
PATH_TMP_TE_ESTM_REGN_PLOT = os.path.join(PATH_TMP_TE, "estmregnplot")
PATH_TMP_TE_ESTM_REAL_GPKG = os.path.join(PATH_TMP_TE, "estmrealgpkg")

CONFINDENCE = 0.3

# final output
PATH_FINAL = '../lake_polygons_test.gpkg'

# for tile
TILE_H = 1024
TILE_W = 1024
STEP = 512

BLANK_RARIO = 0.5
MAYBE_LAKE_RARIO = 0.0001

LOWER_BLUE = numpy.array([ 80,  35,  35])
UPPER_BLUE = numpy.array([130, 255, 255])

