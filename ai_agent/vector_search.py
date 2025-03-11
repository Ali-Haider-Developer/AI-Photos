import os
from dotenv import load_dotenv
import requests
import json
from pathlib import Path

# Load environment variables from the correct path
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# Get configuration with default values
QDRANT_API_URL = os.getenv("QDRANT_API_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "designs")

def search_similar_designs(event_type: str, theme: str):
    """
    Search for similar designs based on event type and theme
    """
    try:
        # Verify configuration
        if not QDRANT_API_URL or not QDRANT_API_KEY:
            print(f"QDRANT_API_URL: {QDRANT_API_URL}")
            print(f"QDRANT_API_KEY: {QDRANT_API_KEY}")
            raise ValueError("Qdrant API configuration missing")

        # Create search endpoint URL
        search_url = f"{QDRANT_API_URL.rstrip('/')}/collections/{QDRANT_COLLECTION}/points/search"

        # Set up headers
        headers = {
            "Content-Type": "application/json",
            "api-key": QDRANT_API_KEY
        }

        # Create query vector (simplified for demo)
        query_text = f"{event_type} {theme}"
        query_vector = generate_query_vector(query_text)

        # Prepare payload
        payload = {
            "vector": query_vector,
            "limit": 5,
            "with_payload": True,
            "with_vectors": True
        }

        # Make request
        print(f"Making request to: {search_url}")
        response = requests.post(
            search_url,
            headers=headers,
            json=payload,
            verify=True  # For HTTPS
        )

        # Check response
        if response.status_code == 200:
            results = response.json().get('result', [])
            return [
                {
                    "url": item.get('payload', {}).get('image_url', '#'),
                    "similarity_score": item.get('score', 0),
                    "metadata": item.get('payload', {}),
                    "image_bytes": item.get('payload', {}).get('image_data', None)
                }
                for item in results
            ]
        else:
            print(f"Qdrant API error: {response.status_code}")
            print(f"Response: {response.text}")
            return []

    except Exception as e:
        print(f"Error in search_similar_designs: {str(e)}")
        return []

def generate_query_vector(text: str, dim: int = 128):
    """
    Generate a simple vector for demo purposes
    In production, use a proper text embedding model
    """
    # Simple hash-based vector generation
    import hashlib
    
    # Create a hash of the text
    hash_object = hashlib.md5(text.encode())
    hash_hex = hash_object.hexdigest()
    
    # Convert hash to vector of floats
    vector = []
    for i in range(dim):
        # Use different parts of the hash to generate vector values
        hash_part = int(hash_hex[i % 32], 16)
        vector.append((hash_part / 15.0) - 0.5)  # Convert to range [-0.5, 0.5]
    
    return vector

def test_qdrant_connection():
    """
    Test the Qdrant connection and configuration
    """
    try:
        # Verify configuration
        if not QDRANT_API_URL:
            print("❌ QDRANT_API_URL is not set in environment variables")
            return False
        if not QDRANT_API_KEY:
            print("❌ QDRANT_API_KEY is not set in environment variables")
            return False

        # Clean the URL
        base_url = QDRANT_API_URL.strip().rstrip('/')
        test_url = f"{base_url}/collections"
        
        headers = {
            "Content-Type": "application/json",
            "api-key": QDRANT_API_KEY
        }
        
        print(f"Testing connection to: {test_url}")
        response = requests.get(test_url, headers=headers, verify=True)
        
        if response.status_code == 200:
            print("✅ Qdrant connection successful!")
            print(f"Available collections: {response.json()}")
            return True
        else:
            print(f"❌ Qdrant connection failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Qdrant connection: {str(e)}")
        print(f"Current QDRANT_API_URL: {QDRANT_API_URL}")
        print(f"Current QDRANT_API_KEY: {'Set' if QDRANT_API_KEY else 'Not Set'}")
        return False 

def create_collection():
    """Create the designs collection if it doesn't exist"""
    try:
        if not QDRANT_API_URL or not QDRANT_API_KEY:
            print("❌ Qdrant configuration missing")
            return False

        base_url = QDRANT_API_URL.strip().rstrip('/')
        
        # First check if collection exists
        check_url = f"{base_url}/collections/{QDRANT_COLLECTION}"
        headers = {
            "Content-Type": "application/json",
            "api-key": QDRANT_API_KEY
        }
        
        check_response = requests.get(check_url, headers=headers)
        
        # If collection exists, return True
        if check_response.status_code == 200:
            print(f"✅ Collection '{QDRANT_COLLECTION}' already exists")
            return True
            
        # If collection doesn't exist (404), create it
        if check_response.status_code == 404:
            # Collection configuration
            payload = {
                "vectors": {
                    "size": 128,  # Vector dimension
                    "distance": "Cosine"  # Distance metric
                }
            }
            
            create_response = requests.put(check_url, headers=headers, json=payload)
            
            if create_response.status_code in [200, 201]:
                print(f"✅ Collection '{QDRANT_COLLECTION}' created successfully")
                return True
            else:
                print(f"❌ Failed to create collection: {create_response.text}")
                return False
        
        print(f"❌ Unexpected status code when checking collection: {check_response.status_code}")
        return False

    except Exception as e:
        print(f"❌ Error managing collection: {str(e)}")
        return False 