# within docker, training

import cv2
import os
import random

from detectron2.checkpoint import DetectionCheckpointer
from detectron2.engine import BestCheckpointer
from detectron2.engine import DefaultTrainer
from detectron2.utils.visualizer import Visualizer
from matplotlib import pyplot as plt
from PIL import Image

from _config import *
from model.config import GetDetectronConfig, TR_DICT, MetadataCatalog


cfg = GetDetectronConfig(preTrained=False)
os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)  # ./output by default
trainer = DefaultTrainer(cfg)
trainer.resume_or_load(resume=False)
trainer.train()
