import os
import random

from detectron2.engine import DefaultPredictor
from detectron2.utils.visualizer import Visualizer
from detectron2.utils.visualizer import ColorMode
from matplotlib import pyplot as plt
from PIL import Image

from _config import *
from model.config import GetDetectronConfig, VA_DICT, MetadataCatalog



cfg = GetDetectronConfig()

cfg.MODEL.WEIGHTS = os.path.join(cfg.OUTPUT_DIR, "model_final.pth")  # path to the model
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.7
predictor = DefaultPredictor(cfg)

for d in random.sample(VA_DICT, 10):
    img = numpy.asarray(Image.open(d["file_name"]))
    out = predictor(img)  # see https://detectron2.readthedocs.io/tutorials/models.html#model-output-format
    v = Visualizer(img, metadata=MetadataCatalog.get("icelake_va"), scale=0.5)
    out = v.draw_instance_predictions(out["instances"].to("cpu"))
    plt.subplot(121)
    plt.imshow(numpy.asarray(Image.open(PATH_TILE_PLOT + d["file_name"].split('/')[-1])))
    plt.subplot(122)
    plt.imshow(out.get_image())
    plt.show()