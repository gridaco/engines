import os
import json
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch.nn.functional as F
import torch


MODEL_PATH = os.path.join(os.path.dirname(__file__), "../data/models")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_PATH)

def get_name_and_confidence(properties, model, tokenizer):
    # Encode the input properties

    # get the 'type' property
    _el = properties['type']
    # remove the 'type' property
    del properties['type']

    _value = json.dumps(properties).replace("{", "").replace("}", "")

    input_text = f"EL: {_el} VALUE: {_value} "

    input_ids = tokenizer.encode(input_text, return_tensors="pt")

    # Create an array of decoder_input_ids filled with the decoder_start_token_id
    decoder_input_ids = torch.full(
        (input_ids.shape[0], model.config.max_length),
        model.config.decoder_start_token_id,
        dtype=torch.long
    )

    # Run the forward pass
    outputs = model(input_ids=input_ids, decoder_input_ids=decoder_input_ids)

    # Extract the logits and apply softmax
    logits = outputs.logits
    softmax_logits = F.softmax(logits, dim=-1)

    # Get the predicted token ids and confidence
    predicted_token_ids = torch.argmax(softmax_logits, dim=-1)
    confidence = softmax_logits.max().item()

    # Decode the output sequence
    new_name = tokenizer.decode(predicted_token_ids[0], skip_special_tokens=False)

    return new_name, confidence


if __name__ == "__main__":

  properties = {
    "type": "div",
    "width": "1px",
    "height": "50px",
    "padding": "10px",
  }

  layer_names_with_confidence = get_name_and_confidence(properties, model, tokenizer)
  print(layer_names_with_confidence)
