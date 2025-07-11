import sys

import torch
from PIL import Image
from transformers import VisionEncoderDecoderModel
from transformers.models.nougat import NougatTokenizerFast

sys.path.append("/Users/dmitryklimov/Code/ML/Karpov/mlservice-lesson-1/ml")
from nougat_latex import NougatLaTexProcessor

model_name = "Norm/nougat-latex-base"
device = "cuda" if torch.cuda.is_available() else "cpu"
# init model
model = VisionEncoderDecoderModel.from_pretrained(model_name).to(device)

# init processor
tokenizer = NougatTokenizerFast.from_pretrained(model_name)

latex_processor = NougatLaTexProcessor.from_pretrained(model_name)

print("Model loaded")

image = Image.open("/Users/dmitryklimov/Code/ML/Karpov/mlservice-lesson-1/ml/examples/ex1.png")
if not image.mode == "RGB":
    image = image.convert('RGB')

pixel_values = latex_processor(image, return_tensors="pt").pixel_values

decoder_input_ids = tokenizer(tokenizer.bos_token, add_special_tokens=False,
                              return_tensors="pt").input_ids
with torch.no_grad():
    outputs = model.generate(
        pixel_values.to(device),
        decoder_input_ids=decoder_input_ids.to(device),
        max_length=model.decoder.config.max_length,
        early_stopping=True,
        pad_token_id=tokenizer.pad_token_id,
        eos_token_id=tokenizer.eos_token_id,
        use_cache=True,
        num_beams=5,
        bad_words_ids=[[tokenizer.unk_token_id]],
        return_dict_in_generate=True,
    )
sequence = tokenizer.batch_decode(outputs.sequences)[0]
sequence = sequence.replace(tokenizer.eos_token, "").replace(tokenizer.pad_token, "").replace(tokenizer.bos_token, "")
print(sequence)
