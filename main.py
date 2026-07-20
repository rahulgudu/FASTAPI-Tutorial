import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Enterprise API with Middleware")


# --- 1. BUILT-IN CORS MIDDLEWARE ---
# This permits frontend applications (like your React app) to make requests to this backend.
origins = [
    "http://localhost:3000",      # Default React/Next.js local server
    "http://127.0.0.1:3000",
    "https://your-company-app.com" # Production frontend domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # Which domains can talk to this backend
    allow_credentials=True,
    allow_methods=["*"],              # Allow GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],              # Allow custom headers like X-Auth-Token
)


# --- 2. CUSTOM TIME & AUDIT LOGGING MIDDLEWARE ---
@app.middleware("http")
async def add_process_time_and_log(request: Request, call_next):
    # --- [A] BEFORE REQUEST PROCESSING ---
    start_time = time.perf_counter()
    print(f"--> [INCOMING] {request.method} request to {request.url.path}")

    # --- [B] PASS REQUEST TO ROUTE / NEXT HANDLER ---
    # Execution pauses here while the route (and Pydantic/Dependencies) processes
    response = await call_next(request)

    # --- [C] AFTER RESPONSE GENERATION ---
    process_time_ms = (time.perf_counter() - start_time) * 1000
    
    # Inject a custom header into the outbound response revealing execution time
    response.headers["X-Process-Time-Ms"] = f"{process_time_ms:.2f}"
    
    print(f"<-- [OUTGOING] Status Code {response.status_code} (Took {process_time_ms:.2f} ms)")
    
    return response


# --- 3. SAMPLE ROUTE TO TEST MIDDLEWARE ---
@app.get("/documents/audit")
async def get_audit_trail():
    # Simulate database processing delay
    time.sleep(0.05)
    return {"status": "Success", "data": "Audit records fetched."}