from fastapi import FastAPI, Depends
from config import Settings, get_settings

app = FastAPI()

@app.get("/info")
async def get_app_info(settings: Settings = Depends(get_settings)):
    # Safely access environment variables with full type hints
    return {
        "app_name": settings.app_name,
        "debug_mode": settings.debug_mode,
        "database": settings.database_url,
        "ai_host": settings.ollama_host
    }