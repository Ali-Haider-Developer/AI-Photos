import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import base64
import os
from dotenv import load_dotenv
from typing import List, Dict
import json

load_dotenv()

TEXT_TO_IMAGE_MODEL = os.getenv("TEXT_TO_IMAGE_MODEL")
FONT_STYLES_MODEL = os.getenv("FONT_STYLES_MODEL")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

class TextStyle:
    def __init__(self, name: str, font: str, color: str, effects: List[str]):
        self.name = name
        self.font = font
        self.color = color
        self.effects = effects

PRESET_STYLES = [
    TextStyle("Modern Minimal", "Helvetica", "#000000", ["shadow", "gradient"]),
    TextStyle("Elegant Script", "Playfair", "#8B4513", ["gold-foil", "3d"]),
    TextStyle("Bold Impact", "Impact", "#FF0000", ["neon", "glow"]),
    TextStyle("Vintage", "Old Standard", "#4A4A4A", ["distressed", "texture"]),
    TextStyle("Artistic", "Brush Script", "#1E90FF", ["watercolor", "handdrawn"])
]

def generate_text_variations(text: str, image_bytes: bytes, num_styles: int = 5) -> List[Dict]:
    """Generate multiple styled versions of text overlay"""
    try:
        # Load original image
        image = Image.open(BytesIO(image_bytes))
        variations = []

        # Generate text styles using AI
        styles = generate_ai_text_styles(text, num_styles)

        for style in styles:
            try:
                # Create styled text image
                styled_image = apply_text_style(image.copy(), text, style)
                
                # Convert to bytes
                img_byte_arr = BytesIO()
                styled_image.save(img_byte_arr, format='PNG')
                img_bytes = img_byte_arr.getvalue()
                
                # Convert to base64
                img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                
                variations.append({
                    "url": f"data:image/png;base64,{img_base64}",
                    "image_bytes": img_bytes,
                    "style_name": style.name,
                    "style_details": {
                        "font": style.font,
                        "color": style.color,
                        "effects": style.effects
                    }
                })
            except Exception as e:
                print(f"Error applying style {style.name}: {str(e)}")
                continue

        return variations

    except Exception as e:
        print(f"Error generating text variations: {str(e)}")
        return []

def generate_ai_text_styles(text: str, num_styles: int) -> List[TextStyle]:
    """Generate text styles using AI"""
    try:
        API_URL = f"https://api-inference.huggingface.co/models/{TEXT_TO_IMAGE_MODEL}"
        headers = {
            "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        prompt = f"Generate {num_styles} unique and creative text styles for: '{text}'. Include font, color, and effects."
        
        response = requests.post(
            API_URL,
            headers=headers,
            json={"inputs": prompt}
        )
        
        if response.status_code == 200:
            # Process AI suggestions
            styles = parse_ai_response(response.json(), num_styles)
            return styles
        
        # Fallback to preset styles if AI fails
        return PRESET_STYLES[:num_styles]
        
    except Exception as e:
        print(f"Error generating AI styles: {str(e)}")
        return PRESET_STYLES[:num_styles]

def apply_text_style(image: Image, text: str, style: TextStyle) -> Image:
    """Apply text style to image"""
    try:
        # Create text overlay with style
        API_URL = f"https://api-inference.huggingface.co/models/{FONT_STYLES_MODEL}"
        headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
        
        # Generate styled text prompt
        style_prompt = f"Create text overlay: '{text}' with {style.name} style, {style.font} font, {style.color} color, effects: {', '.join(style.effects)}"
        
        response = requests.post(
            API_URL,
            headers=headers,
            json={
                "inputs": style_prompt,
                "parameters": {
                    "negative_prompt": "blurry, low quality",
                    "num_inference_steps": 30,
                    "guidance_scale": 7.5
                }
            }
        )
        
        if response.status_code == 200:
            # Merge styled text with original image
            styled_text = Image.open(BytesIO(response.content))
            image.paste(styled_text, (0, 0), styled_text)
            
        return image
        
    except Exception as e:
        print(f"Error applying text style: {str(e)}")
        return image

def parse_ai_response(response: dict, num_styles: int) -> List[TextStyle]:
    """Parse AI response into TextStyle objects"""
    styles = []
    try:
        # Process AI suggestions and create TextStyle objects
        # This is a simplified version - enhance based on actual AI response format
        for i in range(num_styles):
            style = TextStyle(
                name=f"AI Style {i+1}",
                font="Default",
                color="#000000",
                effects=["default"]
            )
            styles.append(style)
    except Exception as e:
        print(f"Error parsing AI response: {str(e)}")
    
    return styles or PRESET_STYLES[:num_styles] 