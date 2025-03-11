from fastapi import APIRouter, HTTPException, UploadFile, File, Response, Form, Request
from fastapi.responses import HTMLResponse, FileResponse
from ai_agent.text_generator import generate_text
from ai_agent.image_generator import generate_image
from ai_agent.image_editor import edit_image, compose_images
from ai_agent.vector_search import search_similar_designs  # Import the vector search function
from ai_agent.workflow import run_ai_workflow  # Import the workflow function
from ai_agent.design_generator import generate_designs
from typing import Dict, Optional, List
import uuid
from datetime import datetime
import base64
from PIL import Image
import io
from ai_agent.text_styler import generate_text_variations, TextStyle
import json
from fastapi.templating import Jinja2Templates
import requests

router = APIRouter()
templates = Jinja2Templates(directory="templates")  # Create templates directory if it doesn't exist

# Store generated images in memory (in production, use a database)
generated_images = {}

# Store designs in memory
designs_db: Dict[str, dict] = {}

@router.post("/generate-text/")
async def generate_text_route(event_type: str, theme: str):
    try:
        result = generate_text(event_type, theme)
        return result
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "fallback_text": {
                    "headline": f"{theme.title()} {event_type}",
                    "tagline": f"Experience the magic of {theme}",
                    "description": f"Join us for an unforgettable {event_type} experience themed around {theme}."
                }
            }
        )

@router.post("/generate-image/")
async def generate_image_route(prompt: str, size: str = "512x512"):
    try:
        width, height = map(int, size.split('x'))
        image_bytes = generate_image(prompt, (width, height))
        
        if image_bytes is None:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate image after multiple attempts. Please try again later."
            )

        # Generate unique ID
        image_id = str(uuid.uuid4())
        
        # Store image with metadata
        designs_db[image_id] = {
            "image": image_bytes,
            "prompt": prompt,
            "size": size,
            "created_at": datetime.now().isoformat(),
            "metadata": {
                "event_type": prompt.split("event_type=")[-1].split("&")[0],
                "theme": prompt.split("theme=")[-1]
            }
        }
        
        # Convert to base64 for display
        image_base64 = base64.b64encode(image_bytes).decode()
        
        html_content = f"""
        <html>
            <head>
                <title>Generated Design</title>
                <style>
                    .container {{
                        max-width: 800px;
                        margin: 0 auto;
                        padding: 20px;
                        font-family: Arial, sans-serif;
                    }}
                    .design-card {{
                        background: white;
                        border-radius: 12px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        padding: 20px;
                        margin-bottom: 20px;
                    }}
                    .image-container {{
                        text-align: center;
                        margin: 20px 0;
                    }}
                    .image-container img {{
                        max-width: 100%;
                        border-radius: 8px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }}
                    .design-info {{
                        background: #f8f9fa;
                        padding: 15px;
                        border-radius: 8px;
                        margin: 15px 0;
                    }}
                    .design-id {{
                        font-family: monospace;
                        background: #e9ecef;
                        padding: 8px 12px;
                        border-radius: 4px;
                        display: inline-block;
                        margin: 10px 0;
                    }}
                    .actions {{
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                        gap: 10px;
                        margin-top: 20px;
                    }}
                    .btn {{
                        background: #4CAF50;
                        color: white;
                        text-decoration: none;
                        padding: 10px 20px;
                        border-radius: 6px;
                        text-align: center;
                        transition: background 0.3s;
                    }}
                    .btn:hover {{
                        background: #45a049;
                    }}
                    .copy-btn {{
                        background: #6c757d;
                        border: none;
                        color: white;
                        padding: 5px 10px;
                        border-radius: 4px;
                        cursor: pointer;
                        margin-left: 10px;
                    }}
                </style>
                <script>
                    function copyId(id) {{
                        navigator.clipboard.writeText(id);
                        alert('ID copied to clipboard!');
                    }}
                </script>
            </head>
            <body>
                <div class="container">
                    <div class="design-card">
                        <h2>Generated Design</h2>
                        
                        <div class="design-info">
                            <h3>Design Details</h3>
                            <p><strong>Event Type:</strong> {designs_db[image_id]['metadata']['event_type']}</p>
                            <p><strong>Theme:</strong> {designs_db[image_id]['metadata']['theme']}</p>
                            <p><strong>Created:</strong> {designs_db[image_id]['created_at']}</p>
                            <p><strong>Size:</strong> {size}</p>
                            <div>
                                <span class="design-id">ID: {image_id}</span>
                                <button onclick="copyId('{image_id}')" class="copy-btn">Copy ID</button>
                            </div>
                        </div>

                        <div class="image-container">
                            <img src="data:image/png;base64,{image_base64}" alt="Generated Design">
                        </div>

                        <div class="actions">
                            <a href="/edit-design/{image_id}" class="btn">Edit Design</a>
                            <a href="/download-design/{image_id}" class="btn">Download Design</a>
                            <a href="/view-design/{image_id}" class="btn">View Details</a>
                        </div>
                    </div>
                </div>
            </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download-design/{design_id}")
async def download_design_route(design_id: str):
    """Download generated design by ID"""
    try:
        if design_id not in designs_db:
            raise HTTPException(status_code=404, detail="Design not found")
        
        design_data = designs_db[design_id]
        image_bytes = design_data["image"]
        filename = f"design_{design_id}.png"
        
        return Response(
            content=image_bytes,
            media_type="image/png",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": "image/png"
            }
        )
    except Exception as e:
        print(f"Download error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/edit-design/{design_id}")
async def edit_design_form(request: Request, design_id: str):
    """Show edit form for a design"""
    try:
        if design_id not in designs_db:
            raise HTTPException(status_code=404, detail="Design not found")
            
        design_data = designs_db[design_id]
        image_base64 = base64.b64encode(design_data["image"]).decode()
        
        return templates.TemplateResponse("edit_form.html", {
            "request": request,
            "design_id": design_id,
            "image_base64": image_base64
        })
        
    except Exception as e:
        print(f"Error loading edit form: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/edit-design/{design_id}")
async def edit_design_route(
    request: Request,
    design_id: str,
    effect: Optional[str] = Form(None),
    text_overlay: Optional[str] = Form(None),
    text_position: Optional[str] = Form("center"),
    text_color: Optional[str] = Form("#ffffff"),
    font_size: Optional[int] = Form(36),
    font_style: Optional[str] = Form("normal"),
    overlay_image: Optional[UploadFile] = File(None),
    overlay_position: Optional[str] = Form("center")
):
    """Apply edits to design"""
    try:
        if design_id not in designs_db:
            raise HTTPException(status_code=404, detail="Design not found")
        
        # Get original image
        original_image = designs_db[design_id]["image"]
        
        # Prepare text style
        text_style = {
            "position": text_position,
            "color": text_color,
            "size": font_size,
            "style": font_style
        }
            
        # Get overlay image if provided
        overlay_bytes = None
        if overlay_image:
            overlay_bytes = await overlay_image.read()
        
        # Apply edits
        edited_image = edit_image(
            original_image,
            effect=effect,
            text_overlay=text_overlay,
            text_style=text_style,
            overlay_image=overlay_bytes,
            overlay_position=overlay_position
        )
        
        # Store edited version
        edited_id = f"{design_id}_edited_{str(uuid.uuid4())[:8]}"
        designs_db[edited_id] = {
            "image": edited_image,
            "parent_id": design_id,
            "created_at": datetime.now().isoformat(),
            "edits": {
                "effect": effect,
                "text": text_overlay,
                "text_style": text_style,
                "has_overlay": overlay_image is not None
            }
        }
        
        # Convert for display
        image_base64 = base64.b64encode(edited_image).decode()
        
        return templates.TemplateResponse("edit_result.html", {
            "request": request,
            "image_base64": image_base64,
            "design_id": edited_id,
            "original_id": design_id
        })
        
    except Exception as e:
        print(f"Edit error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/image/{image_id}")
async def get_image_route(image_id: str):
    try:
        if image_id not in designs_db:
            raise HTTPException(status_code=404, detail="Image not found")
            
        image_data = designs_db[image_id]["image"]
        return Response(content=image_data, media_type="image/png")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search-designs/")
async def search_designs_route(event_type: str, theme: str):
    """
    Generate and showcase designs with their details and IDs
    """
    try:
        # Generate designs using Stable Diffusion
        generated_designs = generate_designs(event_type, theme, num_designs=5)
        
        # Add vector search results if available
        similar_designs = search_similar_designs(event_type, theme)
        
        # Combine both results
        all_designs = generated_designs + similar_designs
        
        html_content = f"""
        <html>
            <head>
                <title>Generated Designs</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background: #f0f2f5;
                        margin: 0;
                        padding: 20px;
                    }}
                    .container {{ 
                        max-width: 1200px; 
                        margin: 0 auto; 
                        padding: 20px;
                    }}
                    .search-header {{
                        background: white;
                        padding: 20px;
                        border-radius: 12px;
                        margin-bottom: 30px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }}
                    .designs-grid {{ 
                        display: grid;
                        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                        gap: 25px;
                    }}
                    .design-card {{
                        background: white;
                        border-radius: 12px;
                        overflow: hidden;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                        transition: transform 0.2s;
                    }}
                    .design-card:hover {{
                        transform: translateY(-5px);
                    }}
                    .design-image-container {{
                        position: relative;
                        padding-top: 75%; /* 4:3 Aspect Ratio */
                    }}
                    .design-image {{ 
                        position: absolute;
                        top: 0;
                        left: 0;
                        width: 100%;
                        height: 100%;
                        object-fit: cover;
                    }}
                    .design-details {{
                        padding: 20px;
                    }}
                    .design-info {{
                        margin-bottom: 15px;
                        color: #666;
                    }}
                    .design-id {{
                        background: #f8f9fa;
                        padding: 12px;
                        border-radius: 8px;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        margin-bottom: 15px;
                    }}
                    .copy-btn {{
                        background: #4CAF50;
                        color: white;
                        border: none;
                        padding: 8px 15px;
                        border-radius: 6px;
                        cursor: pointer;
                        transition: background 0.2s;
                    }}
                    .copy-btn:hover {{
                        background: #45a049;
                    }}
                    .actions {{
                        display: grid;
                        grid-template-columns: 1fr 1fr;
                        gap: 12px;
                    }}
                    .btn {{
                        text-align: center;
                        padding: 10px;
                        border-radius: 6px;
                        text-decoration: none;
                        color: white;
                        font-weight: 500;
                        transition: opacity 0.2s;
                    }}
                    .btn:hover {{
                        opacity: 0.9;
                    }}
                    .edit-btn {{ background: #2196F3; }}
                    .download-btn {{ background: #4CAF50; }}
                    .score-badge {{
                        position: absolute;
                        top: 10px;
                        right: 10px;
                        background: rgba(0,0,0,0.7);
                        color: white;
                        padding: 5px 10px;
                        border-radius: 20px;
                        font-size: 0.9em;
                    }}
                    .design-type {{
                        position: absolute;
                        top: 10px;
                        left: 10px;
                        background: rgba(33, 150, 243, 0.9);
                        color: white;
                        padding: 5px 10px;
                        border-radius: 20px;
                        font-size: 0.8em;
                    }}
                </style>
                <script>
                    function copyId(id) {{
                        navigator.clipboard.writeText(id);
                        const btn = document.getElementById(`copy-${{id}}`);
                        btn.textContent = 'Copied!';
                        setTimeout(() => btn.textContent = 'Copy ID', 2000);
                    }}
                </script>
            </head>
            <body>
                <div class="container">
                    <div class="search-header">
                        <h1>AI-Generated Designs</h1>
                        <p><strong>Event Type:</strong> {event_type}</p>
                        <p><strong>Theme:</strong> {theme}</p>
                        <p><strong>Generated:</strong> {len(generated_designs)} new designs</p>
                    </div>
                    <div class="designs-grid">
                        {generate_design_cards(all_designs)}
                    </div>
                </div>
            </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def generate_design_cards(designs):
    """Helper function to generate HTML for design cards"""
    if not designs:
        return """
            <div style="text-align: center; padding: 30px;">
                <h3>No Designs Found</h3>
                <p>Try different search terms</p>
            </div>
        """
    
    cards = ""
    for design in designs:
        # Use existing ID or generate new one
        design_id = str(uuid.uuid4())
        
        # Store complete design data
        designs_db[design_id] = {
            "image": design.get("image_bytes"),
            "url": design.get("url"),
            "metadata": {
                "event_type": design.get("event_type", "N/A"),
                "theme": design.get("theme", "N/A")
            },
            "similarity_score": design.get("similarity_score", 0),
            "created_at": datetime.now().isoformat()
        }
        
        # Create card HTML
        cards += f"""
            <div class="design-card">
                <div class="design-image-container">
                    <img src="{design['url']}" alt="Design" class="design-image">
                    <span class="score-badge">{design.get('similarity_score', 0):.1f}% Match</span>
                    <span class="design-type">{'AI Generated' if design.get('similarity_score') == 100 else 'Similar'}</span>
                </div>
                <div class="design-details">
                    <div class="design-id">
                        <span>ID: {design_id}</span>
                        <button id="copy-{design_id}" class="copy-btn" onclick="copyId('{design_id}')">Copy ID</button>
                    </div>
                    <div class="actions">
                        <a href="/view-design/{design_id}" class="btn edit-btn">View Design</a>
                        <a href="/download-search-design/{design_id}" class="btn download-btn">Download</a>
                    </div>
                </div>
            </div>
        """
    return cards

@router.get("/view-design/{design_id}")
async def view_design_route(request: Request, design_id: str):
    """View design details and preview"""
    try:
        if design_id not in designs_db:
            raise HTTPException(status_code=404, detail="Design not found")
        
        design_data = designs_db[design_id]
        
        # Handle both URL-based and bytes-based images
        if "url" in design_data:
            image_url = design_data["url"]
            image_display = image_url
        else:
            image_base64 = base64.b64encode(design_data["image"]).decode()
            image_display = f"data:image/png;base64,{image_base64}"
        
        # Get metadata with defaults
        metadata = design_data.get("metadata", {})
        created_at = design_data.get("created_at", "N/A")
        
        return templates.TemplateResponse("view_design.html", {
            "request": request,
            "design_id": design_id,
            "image_display": image_display,
            "created_at": created_at,
            "event_type": metadata.get("event_type", "N/A"),
            "theme": metadata.get("theme", "N/A"),
            "similarity_score": design_data.get("similarity_score", "N/A")
        })
        
    except Exception as e:
        print(f"View error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download-search-design/{design_id}")
async def download_search_design(design_id: str):
    """Download design from search results"""
    try:
        if design_id not in designs_db:
            raise HTTPException(status_code=404, detail="Design not found")
            
        design_data = designs_db[design_id]
        
        # If design has URL, download it first
        if "url" in design_data and design_data["url"]:
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
                response = requests.get(
                    design_data["url"], 
                    timeout=10,
                    headers=headers,
                    allow_redirects=True
                )
                response.raise_for_status()
                image_bytes = response.content
            except Exception as e:
                print(f"Failed to download from URL ({design_data['url']}): {str(e)}")
                # Fallback to stored image bytes if available
                if "image" in design_data and design_data["image"]:
                    image_bytes = design_data["image"]
                else:
                    raise HTTPException(status_code=500, detail="Failed to download image and no backup available")
        # If design has image bytes stored directly
        elif "image" in design_data and design_data["image"]:
            image_bytes = design_data["image"]
        else:
            raise HTTPException(status_code=500, detail="No image data found")
            
        filename = f"design_{design_id}.png"
        
        return Response(
            content=image_bytes,
            media_type="image/png",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": "image/png"
            }
        )
        
    except Exception as e:
        print(f"Download error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
