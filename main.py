from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import Session

from database import engine, Base, get_db

app = FastAPI(title="Enterprise API with Middleware")


class MeetingModel(Base):
    __tablename__ = "meetings"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    agenda = Column(String, nullable = False)
    is_confidential = Column(Boolean, default = False)
    
Base.metadata.create_all(bind=engine)

class MeetingCreate(BaseModel):
    title: str
    agenda: str
    is_confidential: bool = False

class MeetingResponse(BaseModel):
    id: int
    title: str
    agenda: str
    is_confidential: bool

    class Config:
        form_attributes = True
        
@app.post("/meetings", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
async def create_meeting(meeting: MeetingCreate, db: Session = Depends(get_db)):
    
    db_meeting = MeetingModel(
        title=meeting.title,
        agenda=meeting.agenda,
        is_confidential=meeting.is_confidential
    )
    db.add(db_meeting)
    db.commit()
    db.refresh(db_meeting)
    return db_meeting

@app.get("/meetings", response_model=List[MeetingResponse])
async def get_all_meetings(db: Session = Depends(get_db)):
    meetings = db.query(MeetingModel).all()
    return meetings


@app.get("/meetings/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(meeting_id: int, db: Session = Depends(get_db)):
    # Equivalent to SELECT * FROM meetings WHERE id = meeting_id LIMIT 1
    meeting = db.query(MeetingModel).filter(MeetingModel.id == meeting_id).first()
    
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Meeting with ID {meeting_id} not found."
        )
    return meeting


@app.delete("/meetings/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meeting(meeting_id: int, db: Session = Depends(get_db)):
    meeting = db.query(MeetingModel).filter(MeetingModel.id == meeting_id).first()
    
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Meeting with ID {meeting_id} not found."
        )
    
    db.delete(meeting)
    db.commit()
    return