import requests
import json
import os
from dotenv import load_dotenv
from typing import List
import base64
from io import BytesIO
from PIL import Image
import uuid
from datetime import datetime

load_dotenv()

# API Configuration
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
HUGGINGFACE_TEXT_MODEL = os.getenv("HUGGINGFACE_TEXT_MODEL")
HUGGINGFACE_IMAGE_MODEL = os.getenv("HUGGINGFACE_IMAGE_MODEL")

def generate_text_prompt(event_type: str, theme: str) -> str:
    """Generate enhanced prompt using GPT-2"""
    try:
        API_URL = f"https://api-inference.huggingface.co/models/{HUGGINGFACE_TEXT_MODEL}"
        headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
        
        base_prompt = f"Create a {theme} design for a {event_type} event:"
        
        response = requests.post(
            API_URL,
            headers=headers,
            json={"inputs": base_prompt}
        )
        
        if response.status_code == 200:
            enhanced_prompt = response.json()[0]['generated_text']
            return f"{enhanced_prompt}, high quality, professional, detailed"
        
        return base_prompt
        
    except Exception as e:
        print(f"Error generating prompt: {str(e)}")
        return f"Create a {theme} design for a {event_type} event, high quality, professional"

def generate_designs(event_type: str, theme: str, num_designs: int = 5) -> List[dict]:
    """Generate multiple designs using Stable Diffusion"""
    
    API_URL = f"https://api-inference.huggingface.co/models/{HUGGINGFACE_IMAGE_MODEL}"
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = generate_text_prompt(event_type, theme)
    print(f"Using prompt: {prompt}")
    
    designs = []
    try:
        for i in range(num_designs):
            try:
                # Request image generation
                response = requests.post(
                    API_URL,
                    headers=headers,
                    json={
                        "inputs": prompt,
                        "parameters": {
                            "negative_prompt": "low quality, blurry, bad art, text, watermark",
                            "num_inference_steps": 30,
                            "guidance_scale": 7.5,
                            "width": 512,
                            "height": 512
                        }
                    }
                )

                # Check if model is still loading
                if response.status_code == 503:
                    print("Model is loading, waiting for retry...")
                    continue

                # Check for successful response
                if response.status_code != 200:
                    print(f"Image API Error {response.status_code}: {response.text}")
                    continue

                # Get image data
                image_data = response.content
                
                # Create a unique ID
                design_id = str(uuid.uuid4())
                
                # Convert to base64 for URL display
                img_base64 = base64.b64encode(image_data).decode('utf-8')
                img_url = f"data:image/png;base64,{img_base64}"
                
                # Add to designs list
                designs.append({
                    "id": design_id,
                    "url": img_url,
                    "image_bytes": image_data,
                    "similarity_score": 100.0,
                    "metadata": {
                        "event_type": event_type,
                        "theme": theme,
                        "model": HUGGINGFACE_IMAGE_MODEL,
                        "prompt": prompt,
                        "created_at": str(datetime.now())
                    }
                })
                
                print(f"Successfully generated design {i+1}/{num_designs}")
                
            except Exception as img_error:
                print(f"Error processing design {i+1}: {str(img_error)}")
                continue
            
    except Exception as e:
        print(f"Error in design generation: {str(e)}")
        print(f"API URL: {API_URL}")
        print(f"HF Key Set: {'Yes' if HUGGINGFACE_API_KEY else 'No'}")
    
    # If no designs were generated, use placeholders
    if not designs:
        print("Using placeholder designs...")
        designs = generate_placeholder_designs(event_type, theme, num_designs)
    
    return designs

def generate_placeholder_designs(event_type: str, theme: str, num_designs: int) -> List[dict]:
    """Generate placeholder designs when API fails"""
    placeholders = []
    colors = ['#FF5733', '#33FF57', '#3357FF', '#F333FF', '#FF3333']
    
    for i in range(num_designs):
        design_id = str(uuid.uuid4())
        color = colors[i % len(colors)]
        
        # Create a colored placeholder image
        img = Image.new('RGB', (512, 512), color)
        img_io = BytesIO()
        img.save(img_io, format='PNG')
        img_bytes = img_io.getvalue()
        
        # Convert to base64
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        img_url = f"data:image/png;base64,{img_base64}"
        
        placeholders.append({
            "id": design_id,
            "url": img_url,
            "image_bytes": img_bytes,
            "similarity_score": 0.0,
            "metadata": {
                "event_type": event_type,
                "theme": theme,
                "is_placeholder": True,
                "created_at": str(datetime.now())
            }
        })
    
    return placeholders 
