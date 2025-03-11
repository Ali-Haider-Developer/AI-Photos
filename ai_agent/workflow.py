from ai_agent.text_generator import generate_text
from ai_agent.image_generator import generate_image
from ai_agent.image_editor import edit_image
from ai_agent.vector_search import search_similar_designs
from ai_agent.storage import upload_to_supabase

def run_ai_workflow(user_input: dict):
    event_type = user_input.get("event_type")
    theme = user_input.get("theme")
    
    # Step 1: Generate text
    generated_text = generate_text(event_type, theme)
    
    # Step 2: Generate image
    image_prompt = f"{generated_text} - {theme}"
    image_size = "512x512"  # Example size
    generated_image_url = generate_image(image_prompt, image_size)
    
    # Step 3: Edit image (optional)
    edited_image = edit_image(generated_image_url, effect_type="default", text_overlay=generated_text)
    
    # Step 4: Search for similar designs
    similar_designs = search_similar_designs(event_type, theme)
    
    # Step 5: Upload to Supabase
    metadata = {
        "event_type": event_type,
        "theme": theme,
        "generated_text": generated_text,
        "similar_designs": similar_designs
    }
    upload_response = upload_to_supabase(edited_image, metadata)
    
    return {
        "generated_text": generated_text,
        "generated_image_url": generated_image_url,
        "edited_image": edited_image,
        "similar_designs": similar_designs,
        "upload_response": upload_response
    }

def orchestrate_workflow(user_input: dict):
    # Your workflow logic here
    return {"status": "Workflow executed successfully"} 
