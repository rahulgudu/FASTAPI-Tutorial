from ast import List
from datetime import datetime, timedelta, timezone
import os
import shutil
from typing import Optional

from fastapi.staticfiles import StaticFiles
import jwt
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel

app = FastAPI(title="File Uploads & Static Assets")

# Define storage directory path
UPLOAD_DIR = "uploaded_documents"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=UPLOAD_DIR), name="static")

@app.post("/upload-document", status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...)):
    allowed_extensions = [".pdf", ".docx", ".txt", ".png", ".jpg"]
    file_ext = os.path.splitext(file.filename)[1].lower();
    
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported file type. Allowed types: {', '.join(allowed_extensions)}")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {
        "filename": file.filename,
        "file_path": f"/static/{file.filename}",
        "message": "File uploaded successfully."
    }
    
@app.post("/upload-multiple-documents/")
async def upload_multiple_documents(files: List[UploadFile] = File(...)):
    uploaded_records = []

    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        uploaded_records.append({
            "filename": file.filename,
            "public_url": f"/static/{file.filename}"
        })

    return {
        "total_files_uploaded": len(uploaded_records),
        "files": uploaded_records
    }