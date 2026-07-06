from fastapi import FastAPI

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