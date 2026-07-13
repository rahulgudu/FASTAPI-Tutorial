from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field, EmailStr
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


# Pydantic Schema 
class BoardMeetingCreate(BaseModel):
    #standard madetory fields
    title: str
    agenda: str
    
    #Restricitng integer values using Field
    duration_minutes: int = Field(gt=0, le=480, description="Meeting duration in minutes, must be between 1 and 480")
    
    #An optional field (defaults to None if not provided)
    confidential_notes: Optional[str] = None
    
    #Pydantic ntively supports complex types like lists
    attendees: List[str]

#use the schema in fast api routes
@app.post("/meetings/") 
async def create_meeting(meeting: BoardMeetingCreate):
    meeting_dict = meeting.model_dump()
    
    return {"message": "Meeting created successfully", "meeting": meeting_dict}