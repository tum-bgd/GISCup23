import os

from detectron2 import model_zoo
from detectron2.config import get_cfg
from detectron2.data import MetadataCatalog, DatasetCatalog

from .. import PATH_TMP_TR_TR_DICT, PATH_TMP_TR_VA_DICT
from ..utils.Dir import LoadPKL


DatasetCatalog.register("icelake_tr", lambda: LoadPKL(PATH_TMP_TR_TR_DICT))
DatasetCatalog.register("icelake_va", lambda: LoadPKL(PATH_TMP_TR_VA_DICT))
MetadataCatalog.get("icelake_tr").set(thing_classes=["icelake"])
MetadataCatalog.get("icelake_va").set(thing_classes=["icelake"])


def GetDetectronConfig(preTrained=False, preTrainedModelName="model_final.pth"):
    cfg = get_cfg()
    cfg.INPUT.FORMAT = "RGB"  # for statistics
    cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_X_101_32x8d_FPN_3x.yaml"))

    cfg.MODEL.PIXEL_MEAN = [197.84357325, 204.8842635, 208.0415715]
    cfg.MODEL.PIXEL_STD = [0.11537416, 0.10468962, 0.10207428]

    cfg.DATASETS.TRAIN = ("icelake_tr",)
    cfg.DATASETS.TEST = ()
    cfg.DATALOADER.NUM_WORKERS = 1
    cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-InstanceSegmentation/mask_rcnn_X_101_32x8d_FPN_3x.yaml")  # from model zoo
    if preTrained:
        cfg.MODEL.WEIGHTS = os.path.join(cfg.OUTPUT_DIR, preTrainedModelName)
    cfg.SOLVER.IMS_PER_BATCH = 32  # real batch size
    cfg.SOLVER.BASE_LR = 0.00008  # LR
    cfg.SOLVER.MAX_ITER = 10000    # epoch
    cfg.MODEL.RPN.BATCH_SIZE_PER_IMAGE = 3584
    cfg.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE = 3584   # The "RoIHead batch size". 128 is faster, and good enough for this toy dataset (default: 512)
    cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1  # only has one class (icelake)
    cfg.OUTPUT_DIR = "./model/output"
    return cfg
