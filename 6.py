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


# for d in random.sample(TR_DICT, 3):
#     img = numpy.asarray(Image.open(d["file_name"]))
#     visualizer = Visualizer(img, metadata=MetadataCatalog.get("icelake_tr"), scale=0.5)
#     out = visualizer.draw_dataset_dict(d)
#     plt.imshow(out.get_image())
#     plt.show()

# class Trainer(DefaultTrainer):
#     def build_hooks(self):
#         # copy of cfg
#         cfg = self.cfg.clone()
#         # build the original model hooks
#         hooks = super().build_hooks()
#         # add the best checkpointer hook
#         hooks.insert(
#             -1, 
#             BestCheckpointer(
#                 cfg.TEST.EVAL_PERIOD,
#                 DetectionCheckpointer(self.model, cfg.OUTPUT_DIR),
#                 "total_loss",
#                 "min"))
#         return hooks


cfg = GetDetectronConfig(preTrained=False)
os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)  # ./output by default
trainer = DefaultTrainer(cfg)
trainer.resume_or_load(resume=False)
trainer.train()
