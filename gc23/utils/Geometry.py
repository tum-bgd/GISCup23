import cv2
import numpy
import shapely

from gc23 import TILE_W, TILE_H, STEP, LOWER_BLUE, UPPER_BLUE


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
    tl = picHandler.xy(h,          w         )
    tr = picHandler.xy(h,          w+TILE_W-1)
    bl = picHandler.xy(h+TILE_H-1, w         )
    br = picHandler.xy(h+TILE_H-1, w+TILE_W-1)
    return shapely.Polygon((tl, tr, br, bl, tl))


def GetMaybeLakeMask(img):
    cv2HSVimg = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    return cv2.inRange(cv2HSVimg, LOWER_BLUE, UPPER_BLUE)/255


def MaskToPlgn(mask):
    """
    mask: binary mask, will be transformed into uint8 within this func
    """
    mask = mask.astype(numpy.uint8)*255
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    plgns = []
    for contour in contours:
        xs = []
        ys = []
        for point in contour:
            xs.append(int(point[0][0]))
            ys.append(int(point[0][1]))
        plgns.append([xs, ys])
    return plgns


def PlgnToWorldPlgn(picHandler, plgn):
    ws, hs = plgn
    assert len(ws) == len(hs)
    if len(ws) < 4:
        return None
    points = []
    for h, w in zip(hs, ws):
        points.append(picHandler.xy(h, w))
    # start = end
    points[-1] = points[0]
    return shapely.Polygon(points)

