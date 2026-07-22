from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="FastAPI CORS Handling")

# 1. Define allowed origin URLs (Frontend servers)
# Do NOT use ["*"] in production if credentials (cookies/auth headers) are sent!
origins = [
    "http://localhost:3000",      # Default React / Next.js local development server
    "http://127.0.0.1:3000",
    "https://my-company-app.com"   # Production Frontend Domain
]

# 2. Attach CORSMiddleware to the FastAPI instance
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # Specifies allowed domains
    allow_credentials=True,           # Allows cookies & Authorization headers (JWT)
    allow_methods=["*"],              # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],              # Allows all headers (e.g., Content-Type, Authorization)
)

# -------------------------------------------------------------
# SAMPLE ROUTE
# -------------------------------------------------------------
@app.get("/api/data")
async def get_protected_data():
    return {
        "status": "Success",
        "message": "This endpoint can be called from React on http://localhost:3000!"
    }