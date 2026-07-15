from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI();

@app.get("/")
def home():
    return {"message": "Fast api with venv is running fine"}

# params
@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}

# query params: /users?name=John
@app.get("/users")
def get_users(name: str = None): # query params are optional, so we can set default value to None
    return {"name": name}

@app.get("/products")
def get_products(price: float = 20):
    return {"price": price}

# post api
@app.post("/items")
def create_item(item: dict):
    return {"message": "Item created", "item": item}


# Hiding sensitve information and response models
class DocumentCreate(BaseModel):
    title: str
    content: str
    confidential_notes: str
    author_id: int
    system_flags: List[str] = ["internal-draft"]


class DocumentResponse(BaseModel):
    title: str
    content: str


DOCUMENTS_DB = [
    {
        "title": "Q3 Financial Strategy",
        "content": "The company targets a 15% revenue growth in Q3.",
        "confidential_notes": "CEO considering downsizing the marketing team if targets fail.",
        "author_id": 9921,
        "system_flags": ["restricted", "highly-sensitive"]
    }
]

# secure endpoints
@app.get("/documents/public", response_model=List[DocumentResponse])
async def get_public_documents():
    return DOCUMENTS_DB

#privileged endpoints
@app.get("/documents/internal")
async def get_internal_documents():
    return DOCUMENTS_DB