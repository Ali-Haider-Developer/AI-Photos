import os

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://neondb_owner:npg_zAIr4LHybJl6@ep-shrill-bird-a8uol64f-pooler.eastus2.azure.neon.tech/neondb?sslmode=require")

settings = Settings() 
