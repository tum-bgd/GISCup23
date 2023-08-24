import rasterio.mask
from _config import *


mask = geopandas.read_file(PATH_RAW_TRAIN)
for img in ALL_RAW_IMAGE:
    imgName = img.split('_')[3][5:]
    with rasterio.open(PATH_RAW + img, "r") as a:
        for r in ALL_REGION:
            # trX, teX
            maskedImgName = './data/reg/' + imgName + '_' + r['name'] + '_' + TrOrTE(imgName, r['name']) + '.tiff'
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
                maskedPLGName = './data/mask/' + imgName + '_' + r['name'] + '.gpkg'
                tar.to_file(maskedPLGName, driver="GPKG")