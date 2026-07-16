from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field

app = FastAPI()

# --- 1. DEFINE CUSTOM APP-SPECIFIC EXCEPTIONS ---
# Creating custom Python classes allows you to flag specific domain errors easily.
class DatabaseConnectionError(Exception):
    """Raised when the enterprise database fails to respond."""
    def __init__(self, message: str):
        self.message = message

class DocumentAccessDeniedError(Exception):
    """Raised when a user attempts to view highly confidential records."""
    def __init__(self, doc_id: int):
        self.doc_id = doc_id


# --- 2. THE GLOBAL ERROR HANDLERS ---

# Handler A: Catches custom internal database connection issues
@app.exception_handler(DatabaseConnectionError)
async def db_connection_exception_handler(request: Request, exc: DatabaseConnectionError):
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "success": False,
            "error_code": "DATABASE_TEMPORARILY_OFFLINE",
            "message": exc.message,
            "hint": "The infrastructure team has been notified. Retrying shortly."
        }
    )

# Handler B: Catches custom business logic / permission violations
@app.exception_handler(DocumentAccessDeniedError)
async def access_denied_exception_handler(request: Request, exc: DocumentAccessDeniedError):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "success": False,
            "error_code": "CLASSIFIED_ACCESS_VIOLATION",
            "message": f"Access strictly denied for Document ID {exc.doc_id}.",
            "hint": "This incident has been logged. Verify your cleared credentials."
        }
    )

# Handler C: INTERCEPT & OVERRIDE Pydantic's default 422 Validation Error
# By default, Pydantic sends back a verbose, messy array. Let's make it beautiful for the MERN frontend.
@app.exception_handler(RequestValidationError)
async def custom_validation_exception_handler(request: Request, exc: RequestValidationError):
    # Flatten out the Pydantic error array into a clean dictionary mapping fields to messages
    formatted_errors = {}
    for error in exc.errors():
        # error['loc'] gives a tuple like ('body', 'duration_minutes')
        field_name = error['loc'][-1]
        formatted_errors[field_name] = error['msg']

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error_code": "INVALID_REQUEST_PAYLOAD",
            "message": "The data provided failed incoming schema validation checks.",
            "fields": formatted_errors
        }
    )


# --- 3. TEST PATHS ---

class TestSchema(BaseModel):
    title: str = Field(min_length=3)
    duration_minutes: int = Field(gt=0)

@app.post("/test-validation")
async def test_validation_route(payload: TestSchema):
    return {"status": "valid", "data": payload}

@app.get("/trigger-db-error")
async def trigger_db():
    # Simulating a crash when contacting a cluster
    raise DatabaseConnectionError("Connection timeout out after 5000ms.")

@app.get("/trigger-auth-error/{doc_id}")
async def trigger_auth(doc_id: int):
    # Simulating an unauthorized access block
    if doc_id == 99:
        raise DocumentAccessDeniedError(doc_id=99)
    return {"status": "Allowed"}