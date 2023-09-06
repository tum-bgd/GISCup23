from detectron2.engine import DefaultPredictor
from detectron2.engine import DefaultTrainer
from matplotlib import pyplot as plt

from gc23 import TILE_H, TILE_W
from gc23.model.config import *
from gc23.utils.File import LoadImg, LoadJson, ReloadDir, SavePKL
from gc23.utils.Geometry import MaskToPlgn


def Train(loadTrainedModel=False, checkPointModel="model_final.pth"):
    """
    The training process will first load a pre-trained model provided by
    detectron2 library (from Meta). If `isContinue` is true, then the
    trainer will load `checkPointModelName` in `cfg.OUTPUT_DIR` instead
    to continue unfinished training process.
    """
    cfg = GetBaseConfig(_loadTrainedModel=loadTrainedModel, _checkPointModel=checkPointModel)
    os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)
    trainer = DefaultTrainer(cfg)
    trainer.resume_or_load(resume=False)
    trainer.train()


def GetTrainedModel(model, confindence=0.2):
    """
    the model should be within `cfg.OUTPUT_DIR`
    """
    cfg = GetBaseConfig(_loadTrainedModel=True, _checkPointModel=model)
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = confindence
    return DefaultPredictor(cfg)


def GetEstimation(predictor, img):
    assert img.shape == (TILE_H, TILE_W, 3)
    out = predictor(img[:, :, ::-1])  # to BGR mode
    masks = out["instances"].pred_masks.to("cpu")
    scores = out["instances"].scores.to("cpu")
    assert masks.size(0) == scores.size(0)
    return masks.numpy(), scores.numpy()


def GetEstimationByFolder(predictor, srcFolder, tarFolder, plot=False, plotFolder=None, labelFolder=None):
    """
     predictor: trained model
     srcFolder: where the imgs save
     tarFolder: where the estimation (mask + score) save
          plot: whether plot or not
    plotFolder: where the plot save
    """
    ReloadDir(tarFolder)
    if plot:
        ReloadDir(plotFolder)

    for imgFileName in os.listdir(srcFolder):
        thisImg = LoadImg(os.path.join(srcFolder, imgFileName))
        masks, scores = GetEstimation(predictor, thisImg)
        SavePKL([masks, scores], os.path.join(tarFolder, imgFileName.replace('jpg', 'pkl')))
        if plot:
            if labelFolder:
                # with label, maybe validation data, 13
                plt.figure(figsize=(16, 5), dpi=300.0)
                plt.subplot(131)
                plt.imshow(thisImg)
                plt.title("origin img")

                plt.subplot(132)
                plt.imshow(thisImg)
                tileAnnos = LoadJson(os.path.join(labelFolder, imgFileName.replace('jpg', 'json')))["annotations"]
                for tileAnno in tileAnnos:
                    anno = tileAnno["segmentation"][0]
                    xs = anno[0::2]
                    ys = anno[1::2]
                    plt.plot(xs, ys, 'r')
                plt.title("ground truth")

                plt.subplot(133)
                plt.imshow(thisImg)
                for mask in masks:
                    plgns = MaskToPlgn(mask)  # only one actually
                    for xs, ys in plgns:
                        plt.plot(xs, ys, 'b')
                plt.title("estimation")

                plt.savefig(os.path.join(plotFolder, imgFileName), dpi='figure')
                plt.close()
            else:
                # no label, maybe testing data
                plt.figure(figsize=(10.5, 5), dpi=300.0)
                plt.subplot(121)
                plt.imshow(thisImg)
                plt.title("origin img")

                plt.subplot(122)
                plt.imshow(thisImg)
                for mask in masks:
                    plgns = MaskToPlgn(mask)  # only one actually
                    for xs, ys in plgns:
                        plt.plot(xs, ys, 'b')
                plt.title("estimation")

                plt.savefig(os.path.join(plotFolder, imgFileName), dpi='figure')
                plt.close()
