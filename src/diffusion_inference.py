import torch
import numpy as np
import cv2
import pandas as pd
import os
from train_conditional import ConditionalUNet

def generate_stochastic_spreads(num_scenarios=5):
    device = torch.device("cpu")
    model = ConditionalUNet().to(device)
    
    model_path = "models/conditional_wildfire_model.pth"
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()

    df = pd.read_csv('data/processed/metadata_with_weather.csv')
    sample_row = df.iloc[0]
    
    patch_dir = 'data/processed/patches'
    existing_patches = sorted([f for f in os.listdir(patch_dir) if f.endswith('.png')])
    test_patch_path = os.path.join(patch_dir, existing_patches[0])
    
    base_img = cv2.imread(test_patch_path, 0)
    base_img = cv2.resize(base_img, (256, 256))
    base_tensor = torch.from_numpy(base_img).float().unsqueeze(0).unsqueeze(0) / 255.0
    
    # Wind Vector
    rad = np.deg2rad(sample_row['wind_direction'])
    w_speed = sample_row['wind_speed'] / 100.0
    w_vec = torch.tensor([[w_speed * np.cos(rad), w_speed * np.sin(rad)]], dtype=torch.float32)

    print(f"🔥 Generating {num_scenarios} scenarios for Wind: {sample_row['wind_speed']} km/h")

    results = [base_img]
    
    for i in range(num_scenarios):
        # Stochasticity: Noise ko thora control kiya hai (0.05)
        noise = torch.randn_like(base_tensor) * 0.05 
        noisy_input = torch.clamp(base_tensor + noise, 0, 1)
        
        with torch.no_grad():
            prediction = model(noisy_input, w_vec)
        
        # Clean Output Handling
        out_np = (prediction.squeeze().cpu().numpy() * 255).clip(0, 255).astype(np.uint8)
        results.append(out_np)

    os.makedirs('docs', exist_ok=True)
    final_comparison = np.hstack(results)
    cv2.imwrite("docs/stochastic_spread_results.png", final_comparison)
    print("✅ Scenarios saved in 'docs/stochastic_spread_results.png'")

if __name__ == "__main__":
    generate_stochastic_spreads()