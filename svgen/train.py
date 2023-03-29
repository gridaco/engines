import json
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import T5Tokenizer, T5ForConditionalGeneration, T5Config
import pytorch_lightning as pl

class TextToSVGDataset(Dataset):
    def __init__(self, filepath, tokenizer, max_length=512):
        self.filepath = filepath
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.data = []

        with open(filepath, 'r') as file:
            for line in file:
                item = json.loads(line)
                self.data.append((item['name'], item['d']))

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        text, svg = self.data[idx]
        inputs = self.tokenizer.encode_plus(
            text, 
            add_special_tokens=True, 
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        targets = self.tokenizer.encode_plus(
            svg,
            add_special_tokens=True,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        return {
            'input_ids': inputs['input_ids'].squeeze(),
            'attention_mask': inputs['attention_mask'].squeeze(),
            'labels': targets['input_ids'].squeeze()
        }

class TextToSVGModel(pl.LightningModule):
    def __init__(self, config):
        super(TextToSVGModel, self).__init__()
        self.model = T5ForConditionalGeneration.from_pretrained(config.pretrained_model)
        self.tokenizer = T5Tokenizer.from_pretrained(config.pretrained_model)

    def forward(self, input_ids, attention_mask, labels):
        return self.model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)

    def training_step(self, batch, batch_idx):
        input_ids = batch['input_ids']
        attention_mask = batch['attention_mask']
        labels = batch['labels']
        outputs = self(input_ids, attention_mask, labels)
        loss = outputs.loss
        self.log('train_loss', loss)
        return loss

    def configure_optimizers(self):
        return torch.optim.AdamW(self.parameters(), lr=5e-5)

class Config:
    pretrained_model = 't5-small'
    batch_size = 8
    max_length = 512
    filepath = 'train.json'

def main():
    config = Config()
    tokenizer = T5Tokenizer.from_pretrained(config.pretrained_model)
    dataset = TextToSVGDataset(config.filepath, tokenizer, config.max_length)
    train_loader = DataLoader(dataset, batch_size=config.batch_size, shuffle=True, num_workers=4)

    model = TextToSVGModel(config)
    trainer = pl.Trainer(max_epochs=5, gpus=1, progress_bar_refresh_rate=20)
    trainer.fit(model, train_loader)

if __name__ == '__main__':
    main()
