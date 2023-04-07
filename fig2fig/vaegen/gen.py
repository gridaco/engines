# generate.py

import torch
from train import VAE, input_dim, hidden_dim, latent_dim, device

# TODO: load the input_dim

def load_vae_model(model_path, input_dim, hidden_dim, latent_dim):
    model = VAE(input_dim, hidden_dim, latent_dim)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    return model

def generate_random_design(model: VAE, device, num_features, **kwargs):
    (_type, width, height) = (kwargs["type"], kwargs["width"], kwargs["height"])

    model.eval()
    with torch.no_grad():
        z = torch.randn(1, num_features).to(device)
        wh = torch.tensor([[width, height]], device=device, dtype=torch.float32)
        _type = torch.tensor([[_type]], device=device, dtype=torch.float32)
        generated = model.decoder(torch.cat((z, wh, _type), dim=1))
        return generated.cpu().numpy()

# Load the trained model
model_path = "trained_vae.pth"
model = load_vae_model(model_path, input_dim, hidden_dim, latent_dim)

# Generate a random design with specific type, width, and height
_type = 1  # Use an appropriate value for the type
width = 100
height = 100

params = {
    "type": _type,
    "width": width,
    "height": height
}

generated_design = generate_random_design(model, device, latent_dim, **params)
print("Generated design:", generated_design)
