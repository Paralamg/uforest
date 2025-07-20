import torch
from PIL import Image

from .tree_detector.inference import process_geotiff

def make_predict(image: Image, model: dict) -> str:
    coords = process_geotiff("examples/68762df522caa22a41b139a5.tif", model)




    pixel_values = prepare_image(image, model["latex_processor"])
    decoder_input_ids = model["tokenizer"](model["tokenizer"].bos_token, add_special_tokens=False,
                                           return_tensors="pt").input_ids
    with torch.no_grad():
        outputs = model["model"].generate(
            pixel_values.to(model["device"]),
            decoder_input_ids=decoder_input_ids.to(model["device"]),
            max_length=model["model"].decoder.config.max_length,
            early_stopping=True,
            pad_token_id=model["tokenizer"].pad_token_id,
            eos_token_id=model["tokenizer"].eos_token_id,
            use_cache=True,
            num_beams=5,
            bad_words_ids=[[model["tokenizer"].unk_token_id]],
            return_dict_in_generate=True,
        )
    sequence = model["tokenizer"].batch_decode(outputs.sequences)[0]
    sequence = (sequence.replace(model["tokenizer"].eos_token, "")
                .replace(model["tokenizer"].pad_token, "")
                .replace(model["tokenizer"].bos_token, ""))
    return sequence
