from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, Header, status
from pydantic import BaseModel

app = FastAPI()

# A mock user database
VALID_TOKENS = {
    "token_sarah_123": {"name": "Sarah Jenkins", "role": "Admin", "clearance": "Top Secret"},
    "token_alex_456": {"name": "Alex Rivera", "role": "Legal Auditor", "clearance": "Standard"}
}

# The User Schema passed down to routes
class CurrentUser(BaseModel):
    name: str
    role: str
    clearance: str


# --- 1. THE REUSABLE DEPENDENCY FUNCTION ---
# This function handles the heavy lifting: extracting headers and validating tokens.
async def get_current_user(x_auth_token: Optional[str] = Header(None)) -> CurrentUser:
    if not x_auth_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing 'X-Auth-Token' security header."
        )
        
    if x_auth_token not in VALID_TOKENS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or expired session token."
        )
        
    # If valid, return a Pydantic object representing the user
    user_data = VALID_TOKENS[x_auth_token]
    return CurrentUser(**user_data)


# --- 2. ENDPOINTS USING DEPENDENCY INJECTION ---

# Route A: Requires general authentication
@app.get("/documents/board-minutes")
async def get_board_minutes(user: CurrentUser = Depends(get_current_user)):
    # The 'user' variable is automatically injected here after passing validation
    return {
        "message": f"Welcome {user.name} ({user.role}). Access granted to standard minutes.",
        "data": ["Minutes from 2026-02-14", "Minutes from 2026-05-11"]
    }

# Route B: Uses the same dependency, but layers on extra clearance logic inside the endpoint
@app.get("/documents/highly-classified")
async def get_classified_docs(user: CurrentUser = Depends(get_current_user)):
    if user.clearance != "Top Secret":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Security Clearance Level insufficient for these files."
        )
        
    return {
        "message": "Accessing high-security encryption vaults...",
        "owner": user.name
    }