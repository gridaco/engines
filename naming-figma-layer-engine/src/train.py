import json
import torch
import torch.nn as nn
from torch.optim import Adam
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Constants
TRAIN_FILE = "../data/processed.json"
MODEL_NAME = "t5-base"  # or any other compatible seq2seq model

# Dataset


class FigmaDataset(Dataset):
    def __init__(self, file_path, tokenizer):
        with open(file_path, 'r') as f:
            self.data = json.load(f)
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        record = self.data[idx]
        input_features = self.process_record(record)
        input_ids = self.tokenizer.encode(input_features, return_tensors="pt")
        target_ids = self.tokenizer.encode(record['name'], return_tensors="pt")
        return input_ids.squeeze(), target_ids.squeeze()

    @staticmethod
    def process_record(record):
        # Preprocess the record into a suitable format for the model
        # This should include tokenization, one-hot encoding, and other necessary conversions
        input_features = ...
        return input_features

# Model


class FigmaLayerRenamer(nn.Module):
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

# Training


def train(model, dataloader, optimizer, device):
    model.train()
    total_loss = 0.0
    for input_ids, target_ids in dataloader:
        input_ids, target_ids = input_ids.to(device), target_ids.to(device)
        optimizer.zero_grad()
        loss = model(input_ids, target_ids)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    return total_loss / len(dataloader)


# Load data
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
dataset = FigmaDataset(TRAIN_FILE, tokenizer)
dataloader = DataLoader(dataset, batch_size=8, shuffle=True)

# Model setup
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = FigmaLayerRenamer(MODEL_NAME).to(device)
optimizer = Adam(model.parameters(), lr=5e-5)

# Training loop
num_epochs = 10
for epoch in range(num_epochs):
    loss = train(model, dataloader, optimizer, device)
    print(f"Epoch {epoch + 1}/{num_epochs} - Loss: {loss:.4f}")

# Save model
torch.save(model.state_dict(), "figma_layer_renamer.pt")
