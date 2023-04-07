import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from dataset import FigmaNodesDataset
import numpy as np
from tqdm import tqdm

# VAE Model
class VAE(nn.Module):
    def __init__(self, input_dim, hidden_dim, latent_dim):
        super(VAE, self).__init__()

        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, latent_dim * 2),
        )

        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, input_dim),
            nn.Sigmoid(),
        )

    def reparameterize(self, mu, log_var):
        std = torch.exp(0.5 * log_var)
        eps = torch.randn_like(std)
        return mu + eps * std

    def forward(self, x, wh):
        h = self.encoder(x)
        mu, log_var = torch.chunk(h, 2, dim=1)
        z = self.reparameterize(mu, log_var)
        z = torch.cat((z, wh), dim=1)  # Concatenate width and height with the latent variable
        x_recon = self.decoder(z)
        return x_recon, mu, log_var


def vae_loss(recon_x, x, mu, log_var):
    recon_loss = nn.functional.binary_cross_entropy(recon_x, x, reduction='sum')
    kld_loss = -0.5 * torch.sum(1 + log_var - mu.pow(2) - log_var.exp())
    return recon_loss + kld_loss


def train(model, dataloader, device, optimizer, epochs):
    model.train()
    for epoch in range(epochs):
        train_loss = 0
        progress_bar = tqdm(enumerate(dataloader), total=len(dataloader), desc=f"Epoch {epoch + 1}/{epochs}", unit="batch")
        for batch_idx, (data, _, wh) in progress_bar:
            data = data.to(device).float()
            wh = torch.tensor(wh, device=device, dtype=torch.float32)
            optimizer.zero_grad()
            recon_batch, mu, log_var = model(data, wh)
            loss = vae_loss(recon_batch, data, mu, log_var)
            loss.backward()
            train_loss += loss.item()
            optimizer.step()
            progress_bar.set_description(f"Epoch {epoch + 1}/{epochs}, Loss: {train_loss / (batch_idx + 1)}")


# Configuration
hidden_dim = 512
latent_dim = 64
batch_size = 64
epochs = 100
learning_rate = 1e-3
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def main():
    # Load dataset
    db_path = "path/to/your/database"  # Replace this with the path to your dataset
    dataset = FigmaNodesDataset(db_path)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    input_dim = dataset.get_input_dim()

    # Initialize and train VAE
    model = VAE(input_dim, hidden_dim, latent_dim).to(device)
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    train(model, dataloader, device, optimizer, epochs)

    # Save the model
    torch.save(model.state_dict(), "vae_model.pth")
    print("Model saved to vae_model.pth")

if __name__ == "__main__":
    main()