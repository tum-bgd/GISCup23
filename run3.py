import os
os.chdir('./gc23')

from gc23.Data import GetAllRegnEstMask, RegnMaskToWorldPlgn, GetFinalResult


GetAllRegnEstMask(plot=True)
RegnMaskToWorldPlgn()
GetFinalResult()
