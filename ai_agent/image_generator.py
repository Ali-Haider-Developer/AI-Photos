import os
import requests
from dotenv import load_dotenv
from pathlib import Path

# Get the absolute path to the .env file and load it
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

# Get API Key with validation
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
if not HUGGINGFACE_API_KEY:
    raise ValueError("HUGGINGFACE_API_KEY not found in environment variables")

STABLE_DIFFUSION_MODEL = os.getenv("STABLE_DIFFUSION_MODEL", "runwayml/stable-diffusion-v1-5")
API_URL = f"https://api-inference.huggingface.co/models/{STABLE_DIFFUSION_MODEL}"

def generate_image(prompt: str, size: str) -> bytes:
    try:
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
            raise Exception("Authentication failed. Please check your API key.")
        else:
            print(f"❌ Error: {response.text}")
            raise Exception(f"Image generation failed with status code: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error generating image: {str(e)}")
        raise Exception(f"Error generating image: {str(e)}") 