import geopandas
import rasterio.mask
from _config import *


ALL_RAW_IMAGE = [RAW_IMAGE1, RAW_IMAGE2, RAW_IMAGE3, RAW_IMAGE4]

reg = geopandas.read_file(PATH_RAW_REGION)

REGION1 = {'name': '1', 'shape': reg[reg.region_num==1]["geometry"]}
REGION2 = {'name': '2', 'shape': reg[reg.region_num==2]["geometry"]}
REGION3 = {'name': '3', 'shape': reg[reg.region_num==3]["geometry"]}
REGION4 = {'name': '4', 'shape': reg[reg.region_num==4]["geometry"]}
REGION5 = {'name': '5', 'shape': reg[reg.region_num==5]["geometry"]}
REGION6 = {'name': '6', 'shape': reg[reg.region_num==6]["geometry"]}

ALL_REGION = [REGION1, REGION2, REGION3, REGION4, REGION5, REGION6]


mask = geopandas.read_file(PATH_RAW_TRAIN)
for img in ALL_RAW_IMAGE:
    imgName = img.split('_')[3][5:]
    with rasterio.open(PATH_RAW + img, "r") as a:
        for r in ALL_REGION:
            # trX, teX
            maskedImgName = PATH_REGN + imgName + '_' + r['name'] + '_' + TrOrTE(imgName, r['name']) + '.tiff'
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
                maskedPLGName = PATH_PLGN + imgName + '_' + r['name'] + '.gpkg'
                tar.to_file(maskedPLGName, driver="GPKG")