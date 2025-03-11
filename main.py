from fastapi import FastAPI
from api.routes import router as api_router
from ai_agent.workflow import orchestrate_workflow  # Import workflow management
from database.db import engine, Base  # Import database engine and Base

app = FastAPI()

# Create the database tables
Base.metadata.create_all(bind=engine)

app.include_router(api_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Agent API!"}