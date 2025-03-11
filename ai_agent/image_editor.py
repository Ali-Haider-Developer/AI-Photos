from PIL import Image, ImageEnhance, ImageDraw, ImageFont, ImageFilter
import requests
from io import BytesIO
import os
from dotenv import load_dotenv
import io
import time
from typing import Tuple, Optional

load_dotenv()  # Load environment variables from .env file

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
# Primary and fallback models
PRIMARY_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"
FALLBACK_MODEL = "CompVis/stable-diffusion-v1-4"
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

def generate_image(prompt: str, size: Tuple[int, int] = (512, 512)) -> Optional[bytes]:
    """Generate image with fallback and retry mechanism"""
    models = [PRIMARY_MODEL, FALLBACK_MODEL]
    
    for model in models:
        API_URL = f"https://api-inference.huggingface.co/models/{model}"
        headers = {
            "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "negative_prompt": "low quality, blurry, bad art",
                "num_inference_steps": 30,
                "guidance_scale": 7.5,
                "width": size[0],
                "height": size[1]
            }
        }

        for attempt in range(MAX_RETRIES):
            try:
                print(f"🎨 Trying model: {model} (attempt {attempt + 1})")
                response = requests.post(API_URL, headers=headers, json=payload)
                
                if response.status_code == 200:
                    print(f"✅ Successfully generated image with {model}")
                    return response.content
                
                elif response.status_code == 503:
                    print(f"⏳ Model {model} is loading (attempt {attempt + 1}/{MAX_RETRIES})")
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(RETRY_DELAY * (attempt + 1))
                    continue
                
                else:
                    print(f"❌ Error with {model}: {response.status_code}")
                    break  # Try next model
                    
            except Exception as e:
                print(f"❌ Error during attempt {attempt + 1} with {model}: {str(e)}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)

    # If all models fail, generate a placeholder
    print("⚠️ All models failed, generating placeholder")
    return generate_placeholder_image(size, prompt)

def generate_placeholder_image(size: Tuple[int, int], text: str) -> bytes:
    """Generate a placeholder image with text"""
    # Create a new image with a gradient background
    image = Image.new('RGB', size, color='white')
    draw = ImageDraw.Draw(image)
    
    # Add a simple gradient
    for y in range(size[1]):
        r = int(255 * (1 - y/size[1]))
        g = int(200 * (1 - y/size[1]))
        b = int(255 * (y/size[1]))
        for x in range(size[0]):
            draw.point((x, y), fill=(r, g, b))
    
    # Add text
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
        
    draw.text((size[0]/2, size[1]/2), "Image Generation Failed\n" + text, 
              font=font, fill='black', anchor="mm", align="center")
    
    # Convert to bytes
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    return buffer.getvalue()

def edit_image(image_bytes: bytes, effect: str = None, text_overlay: str = None, text_style: dict = None, overlay_image: bytes = None, overlay_position: str = "center") -> bytes:
    """Enhanced image editor with multiple effects and overlays"""
    try:
        image = Image.open(BytesIO(image_bytes)).convert('RGBA')
        
        # 1. Apply visual effects
        if effect:
            image = apply_effect(image, effect)
        
        # 2. Add text overlay with styling
        if text_overlay:
            image = add_styled_text(image, text_overlay, text_style or {})
            
        # 3. Add image overlay if provided
        if overlay_image:
            overlay = Image.open(BytesIO(overlay_image))
            image = compose_images(image, overlay, overlay_position)
            
        # Convert and return
        output = BytesIO()
        image.save(output, format='PNG')
        return output.getvalue()
        
    except Exception as e:
        print(f"Edit error: {str(e)}")
        return image_bytes

def apply_effect(image: Image, effect: str) -> Image:
    """Apply visual effects to image"""
    if effect == "vintage":
        # Sepia tone
        width, height = image.size
        img = image.copy()
        for x in range(width):
            for y in range(height):
                r, g, b = img.getpixel((x, y))[:3]
                tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                img.putpixel((x, y), (min(tr, 255), min(tg, 255), min(tb, 255), 255))
        return img
        
    elif effect == "bright":
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(1.3)
        
    elif effect == "contrast":
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(1.5)
        
    elif effect == "blur":
        return image.filter(ImageFilter.GaussianBlur(radius=2))
        
    return image

def add_styled_text(image: Image, text: str, style: dict) -> Image:
    """Add styled text to image"""
    draw = ImageDraw.Draw(image)
    
    # Get style parameters with defaults
    font_size = style.get('size', 36)
    font_color = style.get('color', 'white')
    position = style.get('position', 'bottom')
    outline = style.get('outline', True)
    
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Calculate text position
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    # Position mapping
    positions = {
        'top': (image.width/2, text_height + 20),
        'bottom': (image.width/2, image.height - text_height - 20),
        'center': (image.width/2, image.height/2),
    }
    x, y = positions.get(position, positions['bottom'])
    x -= text_width/2  # Center horizontally
    
    # Add outline for better visibility
    if outline:
        outline_color = style.get('outline_color', 'black')
        offset = 2
        for dx, dy in [(-offset,-offset), (offset,-offset), (-offset,offset), (offset,offset)]:
            draw.text((x+dx, y+dy), text, font=font, fill=outline_color)
    
    # Draw main text
    draw.text((x, y), text, font=font, fill=font_color)
    
    return image

def compose_images(base_image: Image, overlay_image: Image, position: str = "center", opacity: float = 1.0) -> Image:
    """Compose two images together with positioning"""
    try:
        # Convert images to RGBA for transparency
        base_image = base_image.convert('RGBA')
        overlay_image = overlay_image.convert('RGBA')
        
        # Calculate position coordinates
        base_width, base_height = base_image.size
        overlay_width, overlay_height = overlay_image.size
        
        # Resize overlay if it's too large
        max_overlay_size = (base_width // 2, base_height // 2)
        if overlay_width > max_overlay_size[0] or overlay_height > max_overlay_size[1]:
            overlay_image.thumbnail(max_overlay_size, Image.Resampling.LANCZOS)
            overlay_width, overlay_height = overlay_image.size
        
        # Calculate position
        positions = {
            "center": ((base_width - overlay_width) // 2, (base_height - overlay_height) // 2),
            "top": ((base_width - overlay_width) // 2, 0),
            "bottom": ((base_width - overlay_width) // 2, base_height - overlay_height),
            "left": (0, (base_height - overlay_height) // 2),
            "right": (base_width - overlay_width, (base_height - overlay_height) // 2)
        }
        x, y = positions.get(position, positions["center"])
        
        # Apply opacity
        if opacity < 1.0:
            overlay_image.putalpha(int(255 * opacity))
        
        # Create new image and compose
        composed = Image.new('RGBA', base_image.size)
        composed.paste(base_image, (0, 0))
        composed.paste(overlay_image, (x, y), overlay_image)
        
        return composed.convert('RGB')
        
    except Exception as e:
        print(f"Error composing images: {str(e)}")
        return base_image

def get_image_dimensions(image_bytes: bytes) -> Tuple[int, int]:
    """Get image dimensions"""
    try:
        image = Image.open(BytesIO(image_bytes))
        return image.size
    except Exception as e:
        print(f"Error getting image dimensions: {str(e)}")
        return (0, 0)
