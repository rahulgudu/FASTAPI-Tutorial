from fastapi import FastAPI

app = FastAPI();

@app.get("/")
def home():
    return {"message": "Fast api with venv is running fine"}

# params
@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}