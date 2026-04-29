import boto3
from botocore import UNSIGNED
from botocore.config import Config
import os

s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))
BUCKET_NAME = 'noaa-goes16'

def download_confirmed_file():
    # Exact path found by your snooper
    confirmed_key = "ABI-L1b-RadC/2025/001/00/OR_ABI-L1b-RadC-M6C01_G16_s20250010001173_e20250010003546_c20250010004006.nc"
    
    save_dir = "data/raw/satellite_images"
    if not os.path.exists(save_dir): 
        os.makedirs(save_dir)
    
    local_path = os.path.join(save_dir, os.path.basename(confirmed_key))
    
    print(f"--- FINAL DOWNLOAD ATTEMPT ---")
    print(f"Targeting: {os.path.basename(confirmed_key)}")
    
    try:
        # No more searching, straight to the target
        s3.download_file(BUCKET_NAME, confirmed_key, local_path)
        print(f"\n✅ SUCCESS! File saved at: {local_path}")
        print("Aapki download pipeline ab 100% working hai.")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    download_confirmed_file()