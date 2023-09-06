# train the segmentation model, get estimation on validation dataset and test dataset
# within docker
import argparse
import os
os.chdir('./gc23')

from gc23 import \
    PATH_TMP_TR_VALID, PATH_TMP_TR_VA_ESTM, \
    PATH_TMP_TR_VA_ESTM_PLOT, PATH_TMP_TR_TILE_JSON, \
    PATH_TMP_TE_TILE_MAYBE, PATH_TMP_TE_ESTM, PATH_TMP_TE_ESTM_PLOT

from gc23.model.Op import Train, GetTrainedModel, GetEstimationByFolder


parser = argparse.ArgumentParser(description='specify whether re-training the model')
parser.add_argument('--retrain', default=False, action="store_true", help='flag to re-train a model')
args = parser.parse_args()
if args.retrain:
    print("re-train the segmentation model")
    Train(loadTrainedModel=False)
else:
    print("use trained model")

predictor = GetTrainedModel("model_final_2807.pth", confindence=0.2)
# validation
GetEstimationByFolder(
    predictor,
    PATH_TMP_TR_VALID,
    PATH_TMP_TR_VA_ESTM,
    plot=True,
    plotFolder=PATH_TMP_TR_VA_ESTM_PLOT,
    labelFolder=PATH_TMP_TR_TILE_JSON)
# test
GetEstimationByFolder(
    predictor,
    PATH_TMP_TE_TILE_MAYBE,
    PATH_TMP_TE_ESTM,
    plot=True,
    plotFolder=PATH_TMP_TE_ESTM_PLOT)




