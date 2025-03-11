import os
import requests
from dotenv import load_dotenv
import time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

load_dotenv()  # Load environment variables from .env file

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET")

DATABASE_URL = "postgresql+asyncpg://neondb_owner:npg_zAIr4LHybJl6@ep-shrill-bird-a8uol64f-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"

def create_db_engine():
    retries = 5
    for attempt in range(retries):
        try:
            engine = create_engine(DATABASE_URL)
            # Test the connection
            with engine.connect() as connection:
                connection.execute("SELECT 1")  # Simple query to test connection
            return engine
        except OperationalError as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(2)  # Wait before retrying
    raise Exception("Max retries exceeded while trying to connect to the database.")

def upload_to_supabase(image: bytes, metadata: dict) -> str:
    # Upload image to Supabase storage
    headers = {
        "Authorization": f"Bearer {SUPABASE_API_KEY}",
        "Content-Type": "application/octet-stream"
    }
    
    # Upload the image
    response = requests.post(
        f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/image.png",  # Adjust the path as needed
        headers=headers,
        data=image
    )
    
    if response.status_code == 200:
        # Store metadata in Supabase database
        metadata_response = requests.post(
            f"{SUPABASE_URL}/rest/v1/your_table_name",  # Replace with your table name
            headers={
                "Authorization": f"Bearer {SUPABASE_API_KEY}",
                "Content-Type": "application/json"
            },
            json=metadata
        )
        
        if metadata_response.status_code == 201:
            return "Upload successful"
        else:
            return "Error storing metadata"
    else:
        return "Error uploading image"

def download_from_supabase(image_id: str, format: str) -> bytes:
    # Download image from Supabase storage
    headers = {
        "Authorization": f"Bearer {SUPABASE_API_KEY}"
    }
    
    response = requests.get(
        f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{image_id}.{format}",  # Adjust the path as needed
        headers=headers
    )
    
    if response.status_code == 200:
        return response.content
    else:
        return None  # Handle error appropriately 