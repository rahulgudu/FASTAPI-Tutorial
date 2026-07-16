from typing import List, Optional



from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
app = FastAPI();

@app.get("/")
def home():
    return {"message": "Fast api with venv is running fine"}

# Professional API Status and Custom Responses with error handeling
class DocumentMetadataUpdate(BaseModel):
    title: str
    is_confidential: bool

MOCK_DOCUMENTS = {
    1: {"title": "Document 1", "is_confidential": False},
}


# --- 1. CUSTOM GLOBAL EXCEPTION HANDLER ---
# In Express, this is like global error-handling middleware.
# Here, we override the default 404 behavior to format all 404 responses uniformly.
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == status.HTTP_404_NOT_FOUND:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "success": False,
                "error_code": "RESOURCE_MISSING",
                "message": exc.detail,
                "hint": "Please verify the document identifer and try again."
            }
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail
        }
    )
    
# --- 2. API ROUTES WITH EXPLICIT STATUS CODES ---
@app.get("/documents/{doc_id}", status_code=status.HTTP_200_OK)
async def get_document(doc_id: int):
    if doc_id not in MOCK_DOCUMENTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {doc_id} could not be found."
        )
    return {
        "success": True,
        "data": MOCK_DOCUMENTS[doc_id]
    }
    
@app.put("/documents/{doc_id}", status_code=status.HTTP_200_OK)
async def update_document(doc_id: int, payload: DocumentMetadataUpdate):
    if doc_id not in MOCK_DOCUMENTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {doc_id} could not be found."
        )
    
    
    if MOCK_DOCUMENTS[doc_id]["is_confidential"] and not payload.is_confidential:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security policy violation: Confidential documents cannot be made public arbitrarily."
        )
        
    MOCK_DOCUMENTS[doc_id].update(payload.model_dump())
    return {
        "success": True,
        "message": "Document updated successfully.",
        "data": MOCK_DOCUMENTS[doc_id]
    }