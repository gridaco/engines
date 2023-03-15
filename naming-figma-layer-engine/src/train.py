import os
import json
import torch
import torch.nn as nn
from torch.optim import Adam
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import pytorch_lightning as pl
from pytorch_lightning.callbacks import TQDMProgressBar


# Constants
TRAIN_FILE = os.path.join(os.path.abspath(
    os.path.dirname(__file__)), "../data/processed/train.json")
MODEL_NAME = "t5-small"

# Dataset


class FigmaDataset(Dataset):
    def __init__(self, file_path, tokenizer, max_input_length=128, max_target_length=64):
        with open(file_path, 'r') as f:
            self.data = json.load(f)
        self.tokenizer = tokenizer
        self.max_input_length = max_input_length
        self.max_target_length = max_target_length

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        record = self.data[idx]
        input_features = self.process_record(record)
        input_ids = self.tokenizer.encode(
            input_features, max_length=self.max_input_length, truncation=True, padding="max_length", return_tensors="pt")
        target_ids = self.tokenizer.encode(
            record['name_t'], max_length=self.max_target_length, truncation=True, padding="max_length", return_tensors="pt")
        return input_ids.squeeze(), target_ids.squeeze()

    @staticmethod
    def process_record(record):

        el_str = f"EL: {record['el']} "
        # value_str = f"VALUE: {record['value']} " if record.get('value') else ""
        input_features = f"{el_str}"

        # Preprocess the record into a suitable format for the model
        # This should include tokenization, one-hot encoding, and other necessary conversions
        # type_str = f"TYPE: {record['type']} "
        # color_str = f"COLOR: {record['color']} " if record['color'] else ""
        # background_str = f"BACKGROUND: {record['background']} " if record['background'] else ""
        # text_str = f"TEXT: {record['text']} " if record.get('text') else ""
        # child_count = len(record['children']) if record.get('children') else 0
        # children_str = f"CHILD_COUNT: {child_count} "
        # input_features = f"{type_str}{color_str}{background_str}{text_str}{children_str}"
        return input_features

# Model


class FigmaLayerRenamer(pl.LightningModule):
    def __init__(self, model_name):
        super().__init__()
        self.seq2seq = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    def forward(self, input_ids, target_ids=None):
        if target_ids is not None:
            outputs = self.seq2seq(input_ids=input_ids, labels=target_ids)
            return outputs.loss
        else:
            predicted_ids = self.seq2seq.generate(input_ids=input_ids)
            return predicted_ids

    def training_step(self, batch, batch_idx):
        input_ids, target_ids = batch
        loss = self(input_ids, target_ids)
        self.log("train_loss", loss)
        return loss

    def configure_optimizers(self):
        optimizer = torch.optim.Adam(self.parameters(), lr=5e-5)
        return optimizer


# DataModule
class FigmaDataModule(pl.LightningDataModule):
    def __init__(self, train_file, tokenizer, batch_size=8):
        super().__init__()
        self.train_file = train_file
        self.tokenizer = tokenizer
        self.batch_size = batch_size

    def setup(self, stage=None):
        self.train_dataset = FigmaDataset(self.train_file, self.tokenizer)

    def train_dataloader(self):
        return DataLoader(self.train_dataset, batch_size=self.batch_size, shuffle=True)


# Load data
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
data_module = FigmaDataModule(TRAIN_FILE, tokenizer)

# Model setup
model = FigmaLayerRenamer(MODEL_NAME)

# Training with progress bar
progress_bar = TQDMProgressBar()
trainer = pl.Trainer(max_epochs=10, callbacks=[progress_bar])
trainer.fit(model, data_module)

# Save the trained model
model.seq2seq.save_pretrained(
    os.path.join(os.path.abspath(os.path.dirname(__file__)), "../data/models/"))
