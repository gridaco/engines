import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from torch.nn.utils.rnn import pad_sequence, pack_padded_sequence, pad_packed_sequence
from dataset import FigmaNodesDataset

# Define the Encoder
class Encoder(nn.Module):
    def __init__(self, input_size, hidden_size):
        super(Encoder, self).__init__()
        self.hidden_size = hidden_size
        self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True)

    def forward(self, x, lengths):
        packed_x = pack_padded_sequence(x, lengths, batch_first=True, enforce_sorted=False)
        _, (hidden, cell) = self.lstm(packed_x)
        return hidden, cell

# Define the Decoder with Attention
class Decoder(nn.Module):
    def __init__(self, output_size, hidden_size):
        super(Decoder, self).__init__()
        self.hidden_size = hidden_size
        self.lstm_cell = nn.LSTMCell(output_size, hidden_size)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x, hidden, cell):
        hidden, cell = self.lstm_cell(x, (hidden, cell))
        output = self.fc(hidden)
        return output, hidden, cell

# Define the Seq2Seq Model
class Seq2Seq(nn.Module):
    def __init__(self, input_size, output_size, hidden_size):
        super(Seq2Seq, self).__init__()
        self.encoder = Encoder(input_size, hidden_size)
        self.decoder = Decoder(output_size, hidden_size)

    def forward(self, x, lengths, target=None, teacher_forcing_ratio=0.5):
        batch_size = x.size(0)
        seq_len = lengths.max().item()
        output_size = self.decoder.output_size

        hidden, cell = self.encoder(x, lengths)

        # Initialize the input and outputs
        decoder_input = torch.zeros(batch_size, output_size).to(x.device)
        decoder_outputs = torch.zeros(batch_size, seq_len, output_size).to(x.device)

        # Decode the hidden states
        for t in range(seq_len):
            decoder_output, hidden, cell = self.decoder(decoder_input, hidden, cell)
            decoder_outputs[:, t] = decoder_output

            # Use teacher forcing
            if target is not None and torch.rand(1).item() < teacher_forcing_ratio:
                decoder_input = target[:, t]
            else:
                decoder_input = decoder_output

        return decoder_outputs

# Hyperparameters
input_size = 60  # number of features
output_size = input_size
hidden_size = 128
batch_size = 32
epochs = 10
learning_rate = 0.001

# Load the dataset
sqlite_file = "your_sqlite_file.db"
dataset = FigmaNodesDataset(sqlite_file)

# Split the dataset into train and validation sets
train_size = int(0.8 * len(dataset))
val_size = len(dataset) - train_size
train_dataset, val_dataset = random_split(dataset, [train_size, val_size])

# Create data loaders
def pad_collate(batch):
    (features, children) = zip(*batch)
    lengths = torch.tensor([len(seq) for seq in features])
    features = pad_sequence(features, batch_first=True, padding_value=0)
    children = pad_sequence(children, batch_first=True, padding_value=0)
    return features, lengths, children

train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, collate_fn=pad_collate)
val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, collate_fn=pad_collate)

# Initialize the model, loss function, and optimizer
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = Seq2Seq(input_size, output_size, hidden_size).to(device)
criterion = nn.MSELoss()  # adjust the loss function according to your problem
optimizer = optim.Adam(model.parameters(), lr=learning_rate)

# Training loop
for epoch in range(epochs):
    model.train()
    train_loss = 0.0

    for features, lengths, children in train_loader:
        features, lengths, children = features.to(device), lengths.to(device), children.to(device)

        # Forward pass
        optimizer.zero_grad()
        output = model(features, lengths, target=children)

        # Calculate loss and update weights
        loss = criterion(output, children)
        loss.backward()
        optimizer.step()
        train_loss += loss.item()

    train_loss /= len(train_loader)
    print(f"Epoch {epoch+1}/{epochs}, Train Loss: {train_loss:.6f}")

    # Validation loop
    model.eval()
    val_loss = 0.0

    with torch.no_grad():
        for features, lengths, children in val_loader:
            features, lengths, children = features.to(device), lengths.to(device), children.to(device)

            # Forward pass
            output = model(features, lengths)

            # Calculate loss
            loss = criterion(output, children)
            val_loss += loss.item()

    val_loss /= len(val_loader)
    print(f"Epoch {epoch+1}/{epochs}, Validation Loss: {val_loss:.6f}")
