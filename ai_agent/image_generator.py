import os
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Get the absolute path to the .env file and load it
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

# Get API key with a default value - NO RAISING ERROR HERE
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
if not HUGGINGFACE_API_KEY:
    print("Warning: HUGGINGFACE_API_KEY not found in environment variables")
    HUGGINGFACE_API_KEY = None

STABLE_DIFFUSION_MODEL = os.getenv("STABLE_DIFFUSION_MODEL", "runwayml/stable-diffusion-v1-5")
API_URL = f"https://api-inference.huggingface.co/models/{STABLE_DIFFUSION_MODEL}"

def generate_image(prompt: str, size: str) -> bytes:
    try:
        if not HUGGINGFACE_API_KEY:
            # Return a placeholder image or error response
            return None

        headers = {
            "Authorization": f"Bearer {HUGGINGFACE_API_KEY}"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "size": size
            }
        }
        
        print(f"🎨 Generating image with model: {STABLE_DIFFUSION_MODEL}")
        print(f"🔑 Using API key: {HUGGINGFACE_API_KEY[:10]}...")
        print(f"📝 Prompt: {prompt}")
        
        response = requests.post(API_URL, headers=headers, json=payload)
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            return response.content
        elif response.status_code == 401:
            print("❌ Authentication failed. Please check your API key.")
            return None
        else:
            print(f"❌ Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error generating image: {str(e)}")
        return None 