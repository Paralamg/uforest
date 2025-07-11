import os

import torch
from transformers import VisionEncoderDecoderModel
from transformers.models.nougat import NougatTokenizerFast

from .nougat_latex import NougatLaTexProcessor


def load_model():
    directory = "nougat-latex-base"

    # Если папки с моделью нет, скачать с Huggingface
    model_name = "nougat-latex-base" if os.path.exists(directory) else "Norm/nougat-latex-base"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    # init model
    model = VisionEncoderDecoderModel.from_pretrained(model_name).to(device)

    # init processor
    tokenizer = NougatTokenizerFast.from_pretrained(model_name)

    latex_processor = NougatLaTexProcessor.from_pretrained(model_name)

    return {
        "model": model,
        "tokenizer": tokenizer,
        "latex_processor": latex_processor,
        "device": device
    }
