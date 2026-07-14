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


# Nested Pydantic Models

# 1. Define the child (sub) models first
class DocuementMetaData(BaseModel):
    version: str = Field(default="1.0", pattern=r"^\d+\.\d+$")
    is_confidential: bool = True

class Organizer(BaseModel):
    name: str
    email: EmailStr
    department: str

class AgendaItem(BaseModel):
    title: str
    duration_minutes: int = Field(gt=0, description="Must be a positive integer")
    speaker: str
    
#2 . Define the parent model that nests the sub-models
class DetailedBoardMeeting(BaseModel):
    title: str
    organizer: Organizer
    agenda_items: List[AgendaItem]
    metadata: Optional[DocuementMetaData] = None
    

# 3. Use the parent model in your FastAPI route
@app.post("/meetings/detailed")
async def create_detailed_meeting(meeting: DetailedBoardMeeting):
    # Pydantic validates the entire structure before this code runs.
    # You can access deeply nested attributes using dot notation:
    organizer_email = meeting.organizer.email
    first_item_duration = meeting.agenda_items[0].duration_minutes
    
    return {
        "message": f"Detailed meeting structure validated for '{meeting.title}'",
        "organizer_email": organizer_email,
        "first_agenda_duration": first_item_duration,
        "full_data": meeting.model_dump() # Dumps the entire nested structure into a standard Python dictionary/JSON object
    }