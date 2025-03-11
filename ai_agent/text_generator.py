import os
import requests
import json
import time
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Get the absolute path to the .env file and load it
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

# Get API key with a default value
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
if not HUGGINGFACE_API_KEY:
    print("Warning: HUGGINGFACE_API_KEY not found in environment variables")
    HUGGINGFACE_API_KEY = None

HUGGINGFACE_MODEL = "gpt2"
API_URL = f"https://api-inference.huggingface.co/models/{HUGGINGFACE_MODEL}"

def generate_creative_text(prompt: str, max_retries: int = 3) -> str:
    """Helper function to generate creative text with retries"""
    if not HUGGINGFACE_API_KEY:
        # Return a default response when API key is not available
        return {
            "generated_text": {
                "headline": f"Sample Headline for {prompt}",
                "tagline": f"Sample Tagline for {prompt}",
                "description": f"Sample Description for {prompt}",
                "error": "HUGGINGFACE_API_KEY not configured"
            }
        }

    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_length": 150,
            "temperature": 0.9,
            "top_p": 0.9,
            "do_sample": True,
            "return_full_text": False
        }
    }
    
    print(f"🔑 Using API key: {HUGGINGFACE_API_KEY[:10]}...")
    print(f"🎯 Using model: {HUGGINGFACE_MODEL}")
    
    for attempt in range(max_retries):
        try:
            print(f"🔄 Attempt {attempt + 1} of {max_retries}")
            response = requests.post(API_URL, headers=headers, json=payload)
            print(f"📡 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                return response.json()[0]["generated_text"]
            elif response.status_code == 401:
                print("❌ Authentication failed. Please check your API key.")
                break
            elif response.status_code == 503:
                print("⏳ Model is loading, waiting...")
                time.sleep(2)
                continue
            else:
                print(f"❌ Error: Status code {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error in attempt {attempt + 1}: {str(e)}")
            if attempt == max_retries - 1:
                break
            time.sleep(2)
    
    return {
        "generated_text": {
            "headline": f"Error generating headline for {prompt}",
            "tagline": "Service temporarily unavailable",
            "description": "Please try again later",
            "error": "Failed to generate text after multiple attempts"
        }
    }

def generate_text(event_type: str, theme: str) -> dict:
    """Generate creative text for events with structured output"""
    try:
        # Create prompts for different components
        headline_prompt = f"Create a catchy headline for a {event_type} with the theme '{theme}':"
        tagline_prompt = f"Write a creative tagline for a {theme}-themed {event_type}:"
        description_prompt = f"Write a short description for a {theme}-themed {event_type}:"

        # Generate different components
        headline = generate_creative_text(headline_prompt)
        tagline = generate_creative_text(tagline_prompt)
        description = generate_creative_text(description_prompt)

        # Format the response
        response = {
            "generated_text": {
                "headline": headline.strip() if headline else f"🎯 {theme.title()} {event_type}",
                "tagline": tagline.strip() if tagline else f"Experience the magic of {theme}",
                "description": description.strip() if description else f"Join us for an unforgettable {event_type} experience themed around {theme}.",
                "event_type": event_type,
                "theme": theme
            }
        }

        # Debug logging
        print(f"🎯 Generated content for {event_type} - {theme}")
        print(f"🔹 Headline: {response['generated_text']['headline']}")
        print(f"🔹 Tagline: {response['generated_text']['tagline']}")
        print(f"🔹 Description: {response['generated_text']['description']}")

        return response

    except Exception as e:
        error_msg = f"❌ Error generating text: {str(e)}"
        print(error_msg)
        return {
            "generated_text": {
                "headline": f"🎯 {theme.title()} {event_type}",
                "tagline": f"Experience the magic of {theme}",
                "description": f"Join us for an unforgettable {event_type} experience themed around {theme}.",
                "error": error_msg
            }
        }