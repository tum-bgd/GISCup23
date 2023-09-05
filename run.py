import os
os.chdir('./gc23')

from gc23.Data import PrepareTileLabel, TrVASplit
from gc23.Preprocessing import SplitByRegn, CutTrRegnToTiles, CutTeRegnToTiles

# preprocessing
SplitByRegn(reloadDir=True)
CutTrRegnToTiles(reloadDir=True, plotTile=False)
CutTeRegnToTiles(reloadDir=True)

# prepare for training
PrepareTileLabel(reloadDir=True, plotTile=False)
TrVASplit(trRatio=0.95, reloadDir=True)
