from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel

app = FastAPI(title="FastAPI JWT Authentication")

# -------------------------------------------------------------
# 1. SECURITY CONFIGURATION & HELPERS
# -------------------------------------------------------------
# Secret key to sign JWT tokens (Keep this secret in .env in production!)
SECRET_KEY = "SUPER_SECRET_ENTERPRISE_KEY_CHANGE_IN_PRODUCTION"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing context (Bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme that looks for a Bearer token in the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# -------------------------------------------------------------
# 2. MOCK DATABASE & PYDANTIC MODELS
# -------------------------------------------------------------
# Mock user database (with pre-hashed password for "secret123")
MOCK_USERS_DB = {
    "sarah_jenkins": {
        "username": "sarah_jenkins",
        "email": "sarah@company.com",
        "hashed_password": hash_password("secret123"),
        "role": "Admin",
    }
}


class Token(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    username: str
    email: str
    role: str


# -------------------------------------------------------------
# 3. REUSABLE AUTH DEPENDENCY
# -------------------------------------------------------------
async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserResponse:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode and verify the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None or username not in MOCK_USERS_DB:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user_data = MOCK_USERS_DB[username]
    return UserResponse(
        username=user_data["username"],
        email=user_data["email"],
        role=user_data["role"],
    )


# -------------------------------------------------------------
# 4. API ROUTES
# -------------------------------------------------------------


# LOGIN ROUTE: Receives OAuth2 form data (username & password)
@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = MOCK_USERS_DB.get(form_data.username)

    # Validate user existence and password hash
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create JWT token valid for 30 minutes
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]}
    )

    return {"access_token": access_token, "token_type": "bearer"}


# PROTECTED ROUTE: Requires a valid JWT token
@app.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user