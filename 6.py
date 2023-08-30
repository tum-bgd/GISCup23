import cv2
import os
import pickle
import random

from detectron2 import model_zoo
from detectron2.config import get_cfg
from detectron2.engine import DefaultTrainer
from detectron2.data import MetadataCatalog, DatasetCatalog
from detectron2.utils.visualizer import Visualizer
from matplotlib import pyplot as plt
from PIL import Image


from _config import *


def GetDict(path):
    return pickle.load(open(path, 'rb'))


DatasetCatalog.register("icelake_tr", lambda: GetDict(PATH_TR_DICT))
DatasetCatalog.register("icelake_va", lambda: GetDict(PATH_VA_DICT))
MetadataCatalog.get("icelake_tr").set(thing_classes=["icelake"])
MetadataCatalog.get("icelake_va").set(thing_classes=["icelake"])


# icelake_metadata = MetadataCatalog.get("icelake_tr")
# dataset_dicts = GetDict(PATH_TR_DICT)
# for d in random.sample(dataset_dicts, 3):
#     img = numpy.asarray(Image.open(d["file_name"]))
#     visualizer = Visualizer(img, metadata=icelake_metadata, scale=0.5)
#     out = visualizer.draw_dataset_dict(d)
#     plt.imshow(out.get_image())
#     plt.show()

cfg = get_cfg()
cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
cfg.DATASETS.TRAIN = ("icelake_tr",)
cfg.DATASETS.TEST = ("icelake_va",)
cfg.DATALOADER.NUM_WORKERS = 2
cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")  # from model zoo
cfg.SOLVER.IMS_PER_BATCH = 32  # real batch size
cfg.SOLVER.BASE_LR = 0.00025  # LR
cfg.SOLVER.MAX_ITER = 300    # epoch
# cfg.SOLVER.STEPS = []        # do not decay learning rate
cfg.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE = 256   # The "RoIHead batch size". 128 is faster, and good enough for this toy dataset (default: 512)
cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1  # only has one class (icelake)


os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)  # ./output by default
trainer = DefaultTrainer(cfg)
trainer.resume_or_load(resume=False)
trainer.train()
