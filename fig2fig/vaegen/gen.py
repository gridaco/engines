# generate.py

import torch
from train import VAE, input_dim, hidden_dim, latent_dim, device

def load_vae_model(model_path, input_dim, hidden_dim, latent_dim):
    model = VAE(input_dim, hidden_dim, latent_dim)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    return model

def generate_random_design(model: VAE, device, num_features, width, height):
    model.eval()
    with torch.no_grad():
        z = torch.randn(1, num_features).to(device)
        wh = torch.tensor([[width, height]], device=device, dtype=torch.float32)
        generated = model.decoder(torch.cat((z, wh), dim=1))
        return generated.cpu().numpy()

# Load the trained model
model_path = "trained_vae.pth"
model = load_vae_model(model_path, input_dim, hidden_dim, latent_dim)

# Generate a random design with specific width and height
width = 100
height = 100
generated_design = generate_random_design(model, device, latent_dim, width, height)
print("Generated design:", generated_design)
