from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
from datetime import datetime
import uuid

app = FastAPI()

# ============== Задание 1.1: Базовый маршрут ==============
@app.get("/")
async def root():
    return {"message": "Добро пожаловать в моё приложение FastAPI!"}

# ============== Задание 1.3: Параметры в пути ==============
@app.get("/user/{name}")
async def user_profile(name: str):
    return {"user_name": name, "message": f"Привет, {name}!"}

@app.get("/user/{name}/age/{age}")
async def user_with_age(name: str, age: int):
    return {
        "user_name": name, 
        "age": age,
        "message": f"Привет, {name}! Тебе {age} лет."
    }

# ============== Задание 1.4: Query параметры ==============
@app.get("/search/")
async def search_items(q: str = None, limit: int = 10, sort: str = "asc"):
    return {
        "search_query": q,
        "results_limit": limit,
        "sort_order": sort,
        "message": f"Поиск '{q}' с сортировкой {sort}, лимит {limit}"
    }

@app.get("/products/")
async def get_products(
    category: str = None, 
    min_price: float = 0, 
    max_price: float = 1000000,
    in_stock: bool = True
):
    return {
        "category": category,
        "price_range": {"min": min_price, "max": max_price},
        "in_stock": in_stock,
        "message": f"Товары в категории {category}" if category else "Все товары"
    }

# ============== Задание 1.5: Модели Pydantic и POST ==============
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None
    in_stock: bool = True

class Order(BaseModel):
    items: List[Item]
    customer_name: str
    customer_email: str
    order_date: datetime = datetime.now()


items_db = []
orders_db = []

@app.post("/items/", status_code=status.HTTP_201_CREATED)
async def create_item(item: Item):
    items_db.append(item)
    return {
        "message": "Товар успешно создан",
        "item": item,
        "total_items": len(items_db)
    }

@app.post("/orders/")
async def create_order(order: Order):
    orders_db.append(order)
    total_price = sum(item.price for item in order.items)
    total_tax = sum(item.tax or 0 for item in order.items)
    
    return {
        "order_id": len(orders_db),
        "customer": order.customer_name,
        "total_price": total_price,
        "total_tax": total_tax,
        "final_price": total_price + total_tax,
        "items_count": len(order.items)
    }

@app.get("/items/")
async def get_items():
    return {"items": items_db, "count": len(items_db)}

@app.get("/items/{item_id}")
async def get_item(item_id: int):
    if item_id < 0 or item_id >= len(items_db):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар не найден"
        )
    return items_db[item_id]

# ============== Задание 1.6: Обработка ошибок и валидация ==============
class User(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: str = Field(...)
    age: int = Field(..., ge=0, le=150)
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Неверный формат email')
        return v
    
    @validator('username')
    def validate_username(cls, v):
        if not v.isalnum():
            raise ValueError('Имя пользователя должно содержать только буквы и цифры')
        return v

class Product(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    quantity: int = Field(..., ge=0)

users_db = {}
products_db = {}

@app.post("/users/", status_code=status.HTTP_201_CREATED)
async def create_user(user: User):
    if user.username in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем уже существует"
        )
    
    users_db[user.username] = user
    return {"message": "Пользователь создан", "user": user}

@app.get("/users/{username}")
async def get_user(username: str):
    if username not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь '{username}' не найден"
        )
    return users_db[username]

@app.post("/products/", status_code=status.HTTP_201_CREATED)
async def create_product(product: Product):
    product_id = len(products_db) + 1
    products_db[product_id] = product
    return {"product_id": product_id, "product": product}

@app.get("/products/{product_id}")
async def get_product(product_id: int):
    if product_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID продукта должен быть положительным числом"
        )
    
    if product_id not in products_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Продукт с ID {product_id} не найден"
        )
    
    return products_db[product_id]

# ============== Задание 1.7: Полноценное CRUD приложение ==============
class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    completed: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    priority: int = Field(1, ge=1, le=5)

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[int] = Field(None, ge=1, le=5)

tasks_db: Dict[str, Task] = {}

@app.post("/tasks/", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(task: Task):
    tasks_db[task.id] = task
    return task

@app.get("/tasks/", response_model=List[Task])
async def get_all_tasks(skip: int = 0, limit: int = 10, completed: Optional[bool] = None):
    tasks = list(tasks_db.values())
    
    if completed is not None:
        tasks = [t for t in tasks if t.completed == completed]
    
    tasks = tasks[skip:skip + limit]
    return tasks

@app.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: str):
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Задача с ID {task_id} не найдена"
        )
    return tasks_db[task_id]

@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: str, task_update: TaskUpdate):
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Задача с ID {task_id} не найдена"
        )
    
    task = tasks_db[task_id]
    update_data = task_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(task, field, value)
    
    tasks_db[task_id] = task
    return task

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Задача с ID {task_id} не найдена"
        )
    
    del tasks_db[task_id]
    return {"message": "Задача успешно удалена", "task_id": task_id}

@app.get("/tasks/stats/")
async def get_task_stats():
    total = len(tasks_db)
    completed = len([t for t in tasks_db.values() if t.completed])
    pending = total - completed
    
    return {
        "total_tasks": total,
        "completed_tasks": completed,
        "pending_tasks": pending,
        "completion_rate": (completed / total * 100) if total > 0 else 0
    }

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": request.url.path
        }
    )