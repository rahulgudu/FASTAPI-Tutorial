from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
import sqlite3

from database import get_db_connection, init_db

app = FastAPI(title="Enterprise API with Middleware")


@app.on_event("startup")
def startup_event():
    # Initialize the database when the application starts
    init_db()
    
class MeetingCreate(BaseModel):
    title: str
    agenda: str
    is_confidential: bool = False

class MeetingResponse(BaseModel):
    id: int
    title: str
    agenda: str
    is_confidential: bool

# CRUD operations for board meetings

@app.get("/meetings", response_model=List[MeetingResponse])
async def get_all_meetings(conn: sqlite3.Connection = Depends(get_db_connection)):
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, agenda, is_confidential FROM board_meetings")
    rows = cursor.fetchall()
    
    # Explicitly construct the dictionary for each row
    return [
        dict(row) for row in rows
    ]
    
    
@app.get("/meetings", response_model=List[MeetingResponse])
async def get_all_meetings(conn: sqlite3.Connection = Depends(get_db_connection)):
    cursor = conn.cursor()
    
    
    cursor.execute("SELECT id, title, agenda, is_confidential FROM board_meetings")
    
    rows = cursor.fetchall()
    
    
    return [
        {
            "id": row["id"],
            "title": row["title"],
            "agenda": row["agenda"],
            "is_confidential": bool(row["is_confidential"])
        }
        for row in rows
    ]


@app.get("/meetings/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(meeting_id: int, conn: sqlite3.Connection = Depends(get_db_connection)):
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, title, agenda, is_confidential FROM board_meetings WHERE id = ?", (meeting_id,))
    
    row = cursor.fetchone()
    
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")
    
    return dict(row)

@app.delete("/meetings/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meeting(meeting_id: int, conn: sqlite3.Connection = Depends(get_db_connection)):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM board_meetings WHERE id = ?", (meeting_id,))
    conn.commit()
    
    if cursor.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Meeting with ID {meeting_id} not found."
        )
    return