# AI Event Planning API Documentation

## 📌 API Endpoints

### 1. Text Generation Endpoint
Generate creative text content for events.

**Endpoint:** `POST /generate-text/`

**Input Parameters:**
```json
{
    "event_type": "string",  // Type of event (e.g., "Birthday", "Wedding")
    "theme": "string"        // Theme for the event (e.g., "Modern", "Rustic")
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/generate-text/?event_type=Birthday&theme=Modern"
```

**Example Response:**
```json
{
    "generated_text": {
        "headline": "Modern Minimalist Birthday Bash",
        "tagline": "Celebrate in Contemporary Style",
        "description": "Join us for an unforgettable birthday celebration featuring sleek designs and modern aesthetics."
    }
}
```

### 2. Image Generation Endpoint
Generate AI-powered images for events.

**Endpoint:** `POST /generate-image/`

**Purpose:**
Creates AI-generated images and assigns them unique IDs for future editing.

**Input Parameters:**
```json
{
    "prompt": "string",      // Required: Description of desired image
    "size": "string"         // Optional: Image dimensions (default: "512x512")
}
```

**Response:**
```json
{
    "image_id": "uuid-string",
    "message": "Image generated successfully",
    "image": "binary-image-data"
}
```

### 3. Image Editing Endpoint (`POST /edit-image/{image_id}`)

**Purpose:**
Edit existing images or upload and edit new ones.

**Path Parameters:**
- `image_id`: UUID of previously generated image (optional if uploading new image)

**Form Parameters:**
- `effect`: Type of effect to apply (optional)
- `text_overlay`: Text to overlay on image (optional)
- `uploaded_image`: New image file to upload (optional)

**Example Requests:**

1. Edit Existing Image:
```bash
curl -X POST "http://localhost:8000/edit-image/123e4567-e89b-12d3-a456-426614174000" \
-F "effect=vintage" \
-F "text_overlay=Happy Birthday!"
```

2. Upload and Edit New Image:
```bash
curl -X POST "http://localhost:8000/edit-image/upload" \
-F "uploaded_image=@local_image.png" \
-F "effect=bright" \
-F "text_overlay=Welcome!"
```

**Response:**
```json
{
    "image_id": "uuid-string",
    "message": "Image edited successfully",
    "image": "binary-image-data"
}
```

### Additional Endpoint: Get Image (`GET /image/{image_id}`)

**Purpose:**
Retrieve a previously generated or edited image.

**Path Parameters:**
- `image_id`: UUID of the image to retrieve

**Example:**
```bash
curl -X GET "http://localhost:8000/image/123e4567-e89b-12d3-a456-426614174000" --output image.png
```

### 4. Complete Workflow
Execute the entire event planning workflow.

**Endpoint:** `POST /workflow/`

**Input Parameters:**
```json
{
    "event_type": "string",
    "theme": "string",
    "additional_preferences": {
        "color_scheme": "string",
        "style": "string"
    }
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/workflow/" \
-H "Content-Type: application/json" \
-d '{
    "event_type": "Wedding",
    "theme": "Rustic",
    "additional_preferences": {
        "color_scheme": "Earth tones",
        "style": "Vintage"
    }
}'
```

**Example Response:**
```json
{
    "generated_text": {
        "headline": "Rustic Romance Wedding Celebration",
        "tagline": "Where Vintage Charm Meets Natural Beauty",
        "description": "Experience a magical wedding celebration surrounded by rustic elegance and earthy charm."
    },
    "generated_image_url": "https://storage-url/wedding-image.png",
    "edited_image": "https://storage-url/edited-wedding-image.png",
    "similar_designs": [
        {
            "id": "design1",
            "url": "https://storage-url/similar1.png",
            "similarity_score": 0.89
        }
    ],
    "upload_response": {
        "status": "success",
        "storage_path": "events/wedding-2024/"
    }
}
```

## 🔑 Environment Variables
Required environment variables in `.env` file:
```plaintext
HUGGINGFACE_API_KEY=your_api_key
HUGGINGFACE_MODEL=model_name
STABLE_DIFFUSION_MODEL=model_name
SUPABASE_URL=your_supabase_url
SUPABASE_API_KEY=your_supabase_key
DATABASE_URL=your_database_url
```

## 🛠️ Error Handling
The API includes comprehensive error handling:

- **400 Bad Request**: Invalid input parameters
- **401 Unauthorized**: Invalid API keys
- **500 Internal Server Error**: Server-side processing errors

Example Error Response:
```json
{
    "detail": {
        "error": "Error message here",
        "fallback_text": {
            "headline": "Default Headline",
            "tagline": "Default Tagline",
            "description": "Default Description"
        }
    }
}
```

## 📝 Notes
- Image generation may take a few seconds depending on the model and server load
- Text generation is optimized for event-related content
- All generated content is stored in Supabase for future reference

## 🔄 Detailed Endpoint Workflows

### 1. Text Generation Endpoint (`POST /generate-text/`)

**Purpose:**
Generates creative text content for events using AI language models.

**Input Parameters Explained:**
```json
{
    "event_type": "string",  // Required: Specifies the type of event
    "theme": "string"        // Required: Defines the event's theme
}
```

**Parameter Details:**
- `event_type`: 
  - Purpose: Defines the category of event to generate content for
  - Examples: "Birthday", "Wedding", "Corporate Event", "Conference"
  - Used to: Contextualize the AI's text generation

- `theme`: 
  - Purpose: Specifies the aesthetic or mood of the event
  - Examples: "Modern", "Rustic", "Elegant", "Tropical"
  - Used to: Guide the style and tone of generated content

**Workflow:**
1. Receives event type and theme
2. Processes through AI language model
3. Generates structured text content
4. Returns formatted response

**Example Usage:**
```bash
curl -X POST "http://localhost:8000/generate-text/?event_type=Birthday&theme=Modern"
```

### 2. Image Generation Endpoint (`POST /generate-image/`)

**Purpose:**
Creates AI-generated images based on event descriptions using Stable Diffusion.

**Input Parameters Explained:**
```json
{
    "prompt": "string",      // Required: Description of desired image
    "size": "string"         // Optional: Image dimensions (default: "512x512")
}
```

**Parameter Details:**
- `prompt`:
  - Purpose: Describes the image to be generated
  - Format: Detailed text description
  - Used to: Guide the AI image generation model
  - Example: "Modern birthday party with minimalist decorations and soft lighting"

- `size`:
  - Purpose: Specifies output image dimensions
  - Format: "width x height"
  - Options: "512x512", "768x768", "1024x1024"
  - Used to: Control image resolution and aspect ratio

**Workflow:**
1. Receives image description prompt
2. Processes through Stable Diffusion model
3. Generates image based on description
4. Returns binary image data

**Example Usage:**
```bash
curl -X POST "http://localhost:8000/generate-image/?prompt=Elegant%20wedding%20venue%20with%20floral%20decorations&size=1024x1024" --output event_image.png
```

### 3. Complete Workflow Endpoint (`POST /workflow/`)

**Purpose:**
Orchestrates the entire event planning process, combining text and image generation with design management.

**Input Parameters Explained:**
```json
{
    "event_type": "string",           // Required: Type of event
    "theme": "string",                // Required: Event theme
    "additional_preferences": {        // Optional: Extra customization
        "color_scheme": "string",     // Preferred colors
        "style": "string"             // Specific style preferences
    }
}
```

**Parameter Details:**
- `event_type` & `theme`:
  - Purpose: Same as text generation endpoint
  - Used to: Generate both text and images

- `additional_preferences`:
  - `color_scheme`:
    - Purpose: Specifies color palette
    - Examples: "Earth tones", "Pastels", "Monochrome"
    - Used to: Guide image generation and design

  - `style`:
    - Purpose: Defines specific aesthetic preferences
    - Examples: "Vintage", "Contemporary", "Minimalist"
    - Used to: Refine both text and image generation

**Workflow Steps:**
1. Text Generation:
   - Creates event headlines, taglines, and descriptions
   - Uses event type and theme for context

2. Image Generation:
   - Creates visual content based on text and preferences
   - Incorporates style and color scheme

3. Design Search:
   - Finds similar existing designs
   - Provides inspiration and alternatives

4. Storage:
   - Saves generated content to Supabase
   - Creates permanent URLs for access

**Example Usage:**
```bash
curl -X POST "http://localhost:8000/workflow/" \
-H "Content-Type: application/json" \
-d '{
    "event_type": "Wedding",
    "theme": "Rustic",
    "additional_preferences": {
        "color_scheme": "Earth tones",
        "style": "Vintage"
    }
}'
```

**Example Response:**
```json
{
    "generated_text": {
        "headline": "Rustic Romance Wedding Celebration",
        "tagline": "Where Vintage Charm Meets Natural Beauty",
        "description": "Experience a magical wedding celebration surrounded by rustic elegance and earthy charm."
    },
    "generated_image_url": "https://storage-url/wedding-image.png",
    "edited_image": "https://storage-url/edited-wedding-image.png",
    "similar_designs": [
        {
            "id": "design1",
            "url": "https://storage-url/similar1.png",
            "similarity_score": 0.89
        }
    ],
    "upload_response": {
        "status": "success",
        "storage_path": "events/wedding-2024/"
    }
}
```

## 🔑 Environment Variables
Required environment variables in `.env` file:
```plaintext
HUGGINGFACE_API_KEY=your_api_key
HUGGINGFACE_MODEL=model_name
STABLE_DIFFUSION_MODEL=model_name
SUPABASE_URL=your_supabase_url
SUPABASE_API_KEY=your_supabase_key
DATABASE_URL=your_database_url
```

## 🛠️ Error Handling
The API includes comprehensive error handling:

- **400 Bad Request**: Invalid input parameters
- **401 Unauthorized**: Invalid API keys
- **500 Internal Server Error**: Server-side processing errors

Example Error Response:
```json
{
    "detail": {
        "error": "Error message here",
        "fallback_text": {
            "headline": "Default Headline",
            "tagline": "Default Tagline",
            "description": "Default Description"
        }
    }
}
```

## 📝 Notes
- Image generation may take a few seconds depending on the model and server load
- Text generation is optimized for event-related content
- All generated content is stored in Supabase for future reference

## 🔄 Detailed Endpoint Workflows

### 1. Text Generation Endpoint (`POST /generate-text/`)

**Purpose:**
Generates creative text content for events using AI language models.

**Input Parameters Explained:**
```json
{
    "event_type": "string",  // Required: Specifies the type of event
    "theme": "string"        // Required: Defines the event's theme
}
```

**Parameter Details:**
- `event_type`: 
  - Purpose: Defines the category of event to generate content for
  - Examples: "Birthday", "Wedding", "Corporate Event", "Conference"
  - Used to: Contextualize the AI's text generation

- `theme`: 
  - Purpose: Specifies the aesthetic or mood of the event
  - Examples: "Modern", "Rustic", "Elegant", "Tropical"
  - Used to: Guide the style and tone of generated content

**Workflow:**
1. Receives event type and theme
2. Processes through AI language model
3. Generates structured text content
4. Returns formatted response

**Example Usage:**
```bash
curl -X POST "http://localhost:8000/generate-text/?event_type=Birthday&theme=Modern"
```

### 2. Image Generation Endpoint (`POST /generate-image/`)

**Purpose:**
Creates AI-generated images based on event descriptions using Stable Diffusion.

**Input Parameters Explained:**
```json
{
    "prompt": "string",      // Required: Description of desired image
    "size": "string"         // Optional: Image dimensions (default: "512x512")
}
```

**Parameter Details:**
- `prompt`:
  - Purpose: Describes the image to be generated
  - Format: Detailed text description
  - Used to: Guide the AI image generation model
  - Example: "Modern birthday party with minimalist decorations and soft lighting"

- `size`:
  - Purpose: Specifies output image dimensions
  - Format: "width x height"
  - Options: "512x512", "768x768", "1024x1024"
  - Used to: Control image resolution and aspect ratio

**Workflow:**
1. Receives image description prompt
2. Processes through Stable Diffusion model
3. Generates image based on description
4. Returns binary image data

**Example Usage:**
```bash
curl -X POST "http://localhost:8000/generate-image/?prompt=Elegant%20wedding%20venue%20with%20floral%20decorations&size=1024x1024" --output event_image.png
```

### 3. Complete Workflow Endpoint (`POST /workflow/`)

**Purpose:**
Orchestrates the entire event planning process, combining text and image generation with design management.

**Input Parameters Explained:**
```json
{
    "event_type": "string",           // Required: Type of event
    "theme": "string",                // Required: Event theme
    "additional_preferences": {        // Optional: Extra customization
        "color_scheme": "string",     // Preferred colors
        "style": "string"             // Specific style preferences
    }
}
```

**Parameter Details:**
- `event_type` & `theme`:
  - Purpose: Same as text generation endpoint
  - Used to: Generate both text and images

- `additional_preferences`:
  - `color_scheme`:
    - Purpose: Specifies color palette
    - Examples: "Earth tones", "Pastels", "Monochrome"
    - Used to: Guide image generation and design

  - `style`:
    - Purpose: Defines specific aesthetic preferences
    - Examples: "Vintage", "Contemporary", "Minimalist"
    - Used to: Refine both text and image generation

**Workflow Steps:**
1. Text Generation:
   - Creates event headlines, taglines, and descriptions
   - Uses event type and theme for context

2. Image Generation:
   - Creates visual content based on text and preferences
   - Incorporates style and color scheme

3. Design Search:
   - Finds similar existing designs
   - Provides inspiration and alternatives

4. Storage:
   - Saves generated content to Supabase
   - Creates permanent URLs for access

**Example Usage:**
```bash
curl -X POST "http://localhost:8000/workflow/" \
-H "Content-Type: application/json" \
-d '{
    "event_type": "Wedding",
    "theme": "Rustic",
    "additional_preferences": {
        "color_scheme": "Earth tones",
        "style": "Vintage"
    }
}'
```

**Example Response:**
```json
{
    "generated_text": {
        "headline": "Rustic Romance Wedding Celebration",
        "tagline": "Where Vintage Charm Meets Natural Beauty",
        "description": "Experience a magical wedding celebration surrounded by rustic elegance and earthy charm."
    },
    "generated_image_url": "https://storage-url/wedding-image.png",
    "edited_image": "https://storage-url/edited-wedding-image.png",
    "similar_designs": [
        {
            "id": "design1",
            "url": "https://storage-url/similar1.png",
            "similarity_score": 0.89
        }
    ],
    "upload_response": {
        "status": "success",
        "storage_path": "events/wedding-2024/"
    }
}
```

## 🔑 Environment Variables
Required environment variables in `.env` file:
```plaintext
HUGGINGFACE_API_KEY=your_api_key
HUGGINGFACE_MODEL=model_name
STABLE_DIFFUSION_MODEL=model_name
SUPABASE_URL=your_supabase_url
SUPABASE_API_KEY=your_supabase_key
DATABASE_URL=your_database_url
```

## 🛠️ Error Handling
The API includes comprehensive error handling:

- **400 Bad Request**: Invalid input parameters
- **401 Unauthorized**: Invalid API keys
- **500 Internal Server Error**: Server-side processing errors

Example Error Response:
```json
{
    "detail": {
        "error": "Error message here",
        "fallback_text": {
            "headline": "Default Headline",
            "tagline": "Default Tagline",
            "description": "Default Description"
        }
    }
}
```

## 📝 Notes
- Image generation may take a few seconds depending on the model and server load
- Text generation is optimized for event-related content
- All generated content is stored in Supabase for future reference

## 🔄 Detailed Endpoint Workflows

### 1. Text Generation Endpoint (`POST /generate-text/`)

**Purpose:**
Generates creative text content for events using AI language models.

**Input Parameters Explained:**
```json
{
    "event_type": "string",  // Required: Specifies the type of event
    "theme": "string"        // Required: Defines the event's theme
}
```

**Parameter Details:**
- `event_type`: 
  - Purpose: Defines the category of event to generate content for
  - Examples: "Birthday", "Wedding", "Corporate Event", "Conference"
  - Used to: Contextualize the AI's text generation

- `theme`: 
  - Purpose: Specifies the aesthetic or mood of the event
  - Examples: "Modern", "Rustic", "Elegant", "Tropical"
  - Used to: Guide the style and tone of generated content

**Workflow:**
1. Receives event type and theme
2. Processes through AI language model
3. Generates structured text content
4. Returns formatted response

**Example Usage:**
```bash
curl -X POST "http://localhost:8000/generate-text/?event_type=Birthday&theme=Modern"
```

### 2. Image Generation Endpoint (`POST /generate-image/`)

**Purpose:**
Creates AI-generated images based on event descriptions using Stable Diffusion.

**Input Parameters Explained:**
```json
{
    "prompt": "string",      // Required: Description of desired image
    "size": "string"         // Optional: Image dimensions (default: "512x512")
}
```

**Parameter Details:**
- `prompt`:
  - Purpose: Describes the image to be generated
  - Format: Detailed text description
  - Used to: Guide the AI image generation model
  - Example: "Modern birthday party with minimalist decorations and soft lighting"

- `size`:
  - Purpose: Specifies output image dimensions
  - Format: "width x height"
  - Options: "512x512", "768x768", "1024x1024"
  - Used to: Control image resolution and aspect ratio

**Workflow:**
1. Receives image description prompt
2. Processes through Stable Diffusion model
3. Generates image based on description
4. Returns binary image data

**Example Usage:**
```bash
curl -X POST "http://localhost:8000/generate-image/?prompt=Elegant%20wedding%20venue%20with%20floral%20decorations&size=1024x1024" --output event_image.png
```

### 3. Complete Workflow Endpoint (`POST /workflow/`)

**Purpose:**
Orchestrates the entire event planning process, combining text and image generation with design management.

**Input Parameters Explained:**
```json
{
    "event_type": "string",           // Required: Type of event
    "theme": "string",                // Required: Event theme
    "additional_preferences": {        // Optional: Extra customization
        "color_scheme": "string",     // Preferred colors
        "style": "string"             // Specific style preferences
    }
}
```

**Parameter Details:**
- `event_type` & `theme`:
  - Purpose: Same as text generation endpoint
  - Used to: Generate both text and images

- `additional_preferences`:
  - `color_scheme`:
    - Purpose: Specifies color palette
    - Examples: "Earth tones", "Pastels", "Monochrome"
    - Used to: Guide image generation and design

  - `style`:
    - Purpose: Defines specific aesthetic preferences
    - Examples: "Vintage", "Contemporary", "Minimalist"
    - Used to: Refine both text and image generation

**Workflow Steps:**
1. Text Generation:
   - Creates event headlines, taglines, and descriptions
   - Uses event type and theme for context

2. Image Generation:
   - Creates visual content based on text and preferences
   - Incorporates style and color scheme

3. Design Search:
   - Finds similar existing designs
   - Provides inspiration and alternatives

4. Storage:
   - Saves generated content to Supabase
   - Creates permanent URLs for access

**Example Usage:**
```bash
curl -X POST "http://localhost:8000/workflow/" \
-H "Content-Type: application/json" \
-d '{
    "event_type": "Wedding",
    "theme": "Rustic",
    "additional_preferences": {
        "color_scheme": "Earth tones",
        "style": "Vintage"
    }
}'
```

**Example Response:**
```json
{
    "generated_text": {
        "headline": "Rustic Romance Wedding Celebration",
        "tagline": "Where Vintage Charm Meets Natural Beauty",
        "description": "Experience a magical wedding celebration surrounded by rustic elegance and earthy charm."
    },
    "generated_image_url": "https://storage-url/wedding-image.png",
    "edited_image": "https://storage-url/edited-wedding-image.png",
    "similar_designs": [
        {
            "id": "design1",
            "url": "https://storage-url/similar1.png",
            "similarity_score": 0.89
        }
    ],
    "upload_response": {
        "status": "success",
        "storage_path": "events/wedding-2024/"
    }
}
```

## 🔑 Environment Variables
Required environment variables in `.env` file:
```plaintext
HUGGINGFACE_API_KEY=your_api_key
HUGGINGFACE_MODEL=model_name
STABLE_DIFFUSION_MODEL=model_name
SUPABASE_URL=your_supabase_url
SUPABASE_API_KEY=your_supabase_key
DATABASE_URL=your_database_url
```

## 🛠️ Error Handling
The API includes comprehensive error handling:

- **400 Bad Request**: Invalid input parameters
- **401 Unauthorized**: Invalid API keys
- **500 Internal Server Error**: Server-side processing errors

Example Error Response:
```json
{
    "detail": {
        "error": "Error message here",
        "fallback_text": {
            "headline": "Default Headline",
            "tagline": "Default Tagline",
            "description": "Default Description"
        }
    }
}
```

## 📝 Notes
- Image generation may take a few seconds depending on the model and server load
### Data Flow:
1. **Input Validation:**
   - All parameters are validated before processing
   - Invalid inputs return 400 Bad Request

2. **AI Processing:**
   - Text generation uses GPT models
   - Image generation uses Stable Diffusion
   - Processing times vary by request complexity

3. **Error Handling:**
   - Comprehensive error catching
   - Fallback responses for failures
   - Detailed error messages for debugging

4. **Response Formatting:**
   - Text responses in JSON format
   - Images as binary data with proper headers
   - Workflow responses include all generated content

### Best Practices:
- Use specific, detailed prompts for better results
- Consider image size impacts on generation time
- Include error handling in your client code
- Store generated content IDs for future reference
