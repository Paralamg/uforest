import os

import torch
from .tree_detector.model import TreeSegmentationService


def load_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    # init model
    model = TreeSegmentationService(model_dir="models/rcnn_R_101")

    return {
        "model": model,
        "device": device
    }
