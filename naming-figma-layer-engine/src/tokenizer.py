import os
from transformers import AutoTokenizer

MODEL_NAME = "t5-small"
MODEL_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../data/models/")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
tokenizer.save_pretrained(MODEL_PATH)