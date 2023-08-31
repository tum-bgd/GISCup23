from . import *

import pickle

from detectron2 import model_zoo
from detectron2.config import get_cfg
from detectron2.data import MetadataCatalog, DatasetCatalog


def GetDict(path):
    return pickle.load(open(path, 'rb'))


TR_DICT = GetDict(PATH_TR_DICT)
VA_DICT = GetDict(PATH_VA_DICT)
DatasetCatalog.register("icelake_tr", lambda: GetDict(PATH_TR_DICT))
DatasetCatalog.register("icelake_va", lambda: GetDict(PATH_VA_DICT))
MetadataCatalog.get("icelake_tr").set(thing_classes=["icelake"])
MetadataCatalog.get("icelake_va").set(thing_classes=["icelake"])


def GetDetectronConfig():
    cfg = get_cfg()
    cfg.INPUT.FORMAT = "RGB"
    cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))

    cfg.MODEL.PIXEL_MEAN = [197.84357325, 204.8842635, 208.0415715]
    cfg.MODEL.PIXEL_STD = [0.11537416, 0.10468962, 0.10207428]

    cfg.DATASETS.TRAIN = ("icelake_tr",)
    # cfg.DATASETS.TEST = ("icelake_va",)
    cfg.DATALOADER.NUM_WORKERS = 1
    cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")  # from model zoo
    cfg.SOLVER.IMS_PER_BATCH = 16  # real batch size
    cfg.SOLVER.BASE_LR = 0.001  # LR
    cfg.SOLVER.MAX_ITER = 800    # epoch
    # cfg.SOLVER.STEPS = []        # do not decay learning rate
    cfg.MODEL.RPN.BATCH_SIZE_PER_IMAGE = 1024
    cfg.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE = 1024   # The "RoIHead batch size". 128 is faster, and good enough for this toy dataset (default: 512)
    cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1  # only has one class (icelake)
    return cfg


if __name__ == '__main__':
    print(GetDetectronConfig())
