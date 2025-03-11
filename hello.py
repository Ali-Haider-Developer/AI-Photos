from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from ai_agent.vector_search import test_qdrant_connection, create_collection

app = FastAPI(title="ALI HAIDER AI Agent", description="The job of this AI agent is to generate a photo for us according to our details.", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    try:
        # Test Qdrant connection
        connection_success = test_qdrant_connection()
        if connection_success:
            # Create collection if it doesn't exist
            create_collection()
        else:
            print("⚠️ Warning: Qdrant connection test failed")
    except Exception as e:
        print(f"⚠️ Error during startup: {str(e)}")
        # Continue running even if Qdrant setup fails

app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "My name is Ali Haider and I am an agent AI developer and if you need any kind of development help, please contact us.!"}

# This is important for Vercel
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)