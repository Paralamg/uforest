import torch
from detectron2.engine import DefaultPredictor
from .config import get_model_cfg


class TreeSegmentationService:
    def __init__(self, model_dir: str = "../models/rcnn_R_101"):
        cfg = get_model_cfg(model_dir)
        self.cfg = cfg
    
        self.predictor = DefaultPredictor(cfg)

    def predict(self, image):
        torch.cuda.empty_cache()
        return self.predictor(image)
