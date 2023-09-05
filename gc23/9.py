# within docker, for te

import os
import pickle
import random
import torch

from detectron2.data import build_detection_test_loader
from detectron2.engine import DefaultPredictor
from detectron2.evaluation import COCOEvaluator, inference_on_dataset
from detectron2.utils.visualizer import Visualizer
from detectron2.utils.visualizer import ColorMode
from matplotlib import pyplot as plt
from PIL import Image

from _config import *
from gc23.utils.Dir import ReloadDir
from model.config import GetDetectronConfig, VA_DICT, MetadataCatalog


def GetEstimation(predictor, img):
    assert img.shape == (TILE_H, TILE_W, 3)
    out = predictor(img[:, :, ::-1])  # to BGR mode
    masks = out["instances"].pred_masks.to("cpu")
    scores = out["instances"].scores.to("cpu")
    assert masks.size(0) == scores.size(0)
    return masks.numpy(), scores.numpy()


cfg = GetDetectronConfig(preTrained=True, preTrainedModelName="model_final_2807.pth")
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.2
predictor = DefaultPredictor(cfg)

# evaluator = COCOEvaluator("icelake_va", output_dir="./output_va")
# val_loader = build_detection_test_loader(cfg, "icelake_va")
# print(inference_on_dataset(predictor.model, val_loader, evaluator))

ReloadDir(PATH_OUT_TILE_PLOT)
for imgName in os.listdir(PATH_OUT_TILE_MAYBE):
    img = numpy.asarray(Image.open(PATH_OUT_TILE_MAYBE + imgName))
    out = predictor(img[:, :, ::-1])  # to BGR mode
    v = Visualizer(img, metadata=MetadataCatalog.get("icelake_va"), scale=1.0)
    out = v.draw_instance_predictions(out["instances"].to("cpu"))
    plt.figure(figsize=(10.5, 5), dpi=200.0)
    plt.subplot(121)
    plt.imshow(img)
    plt.subplot(122)
    plt.imshow(out.get_image())
    plt.savefig(PATH_OUT_TILE_PLOT + imgName, dpi='figure')
    plt.close()
