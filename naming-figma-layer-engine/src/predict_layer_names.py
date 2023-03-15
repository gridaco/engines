import os
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

MODEL_NAME = os.path.join(os.path.dirname(__file__), "../data/models/???")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)




def generate_layer_names(properties, model, tokenizer, top_k=5):
    input_text = "Properties: "
    for key, value in properties.items():
        input_text += f"{key}: {value} "

    input_ids = tokenizer.encode(input_text, return_tensors="pt")
    
    # Generate predictions
    with torch.no_grad():
        outputs = model.generate(input_ids, num_return_sequences=top_k, num_beams=top_k, temperature=0.7)

    # Decode the predicted layer names
    predicted_names = [tokenizer.decode(output, skip_special_tokens=True) for output in outputs]

    # Calculate confidence scores
    logits = outputs.logits
    probs = torch.softmax(logits, dim=-1)
    top_probs, _ = torch.topk(probs, top_k, dim=-1)
    confidence_scores = top_probs.mean(dim=-1).tolist()

    # Return the layer names along with their confidence scores
    return list(zip(predicted_names, confidence_scores))


if __name__ == "__main__":

  properties = {
      "color": "red",
      "background": "white",
      "width": "100px",
      "height": "50px",
  }

  layer_names_with_confidence = generate_layer_names(properties, model, tokenizer)
  print(layer_names_with_confidence)
