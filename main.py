from fastapi import FastAPI,HTTPException, status
from enum import Enum;
from typing import List, Optional
from pydantic import BaseModel, Field
app = FastAPI(title="To-Do CRUD API");

# --- 1. PYDANTIC MODELS (Your Mongoose Equivalents) ---
class PriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class SubTask(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    is_completed: bool = False
    
# the primary schema for creating/updating tasks (Nested Structutre)
class Task(BaseModel):
    id: int
    title: str = Field(min_lenght = 3, max_length=50, description="Title must be between 3 and 50 characters")
    description: Optional[str] = Field(None, max_length=20)
    priority: PriorityEnum = PriorityEnum.medium
    is_completed: bool = False
    subtasks: List[SubTask] = []
    
# --- 2. IN-MEMORY DATABASE ---
TODO_DB: List[Task] = []

# --- 3. CRUD Routes ---
# CREATE: Add a new task
@app.post("/tasks/", response_model=Task, status_code = status.HTTP_201_CREATED)
async def create_task(task: Task):
    for existitng_task in TODO_DB:
        if existitng_task.id == task.id:
            raise HTTPException(status_code=400, detail=f"Task with ID {task.id} already exists.")
    TODO_DB.append(task)
    return task

# READ ALL: Get tasks (with an optional query parameter to filter by priority)
@app.get("/tasks/", response_model=List[Task])
async def get_tasks(priority: Optional[PriorityEnum] = None):
    if priority:
        filtered_tasks = [task for task in TODO_DB if task.priority == priority]
        return filtered_tasks
    return TODO_DB

# READ ONE: Get a specific task using a Dynamic Path Parameter
@app.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: int):
    for task in TODO_DB:
        if task.id == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")

# UPDATE: Modify an existing task by its ID
@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: int, updated_task: Task):
    for index, task in enumerate(TODO_DB):
        if task.id == task_id:
            TODO_DB[index] = updated_task
            return updated_task
    raise HTTPException(status_code=404, detail="Task not found")
    
# DELETE: Remove a task by its ID
@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int):
    for index, task in enumerate(TODO_DB):
        if task.id == task_id:
            TODO_DB.pop(index)
            return
    raise HTTPException(status_code=404, detail="Task not found")