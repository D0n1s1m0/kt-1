import requests
import json

BASE_URL = "http://localhost:8000"

def test_all_endpoints():
    """Тестирование всех эндпоинтов"""
    print("=" * 50)
    print("ТЕСТИРОВАНИЕ FASTAPI ПРИЛОЖЕНИЯ")
    print("=" * 50)
    
    # 1. Тест корневого маршрута
    print("\n1. Корневой маршрут:")
    response = requests.get(f"{BASE_URL}/")
    print(f"   Статус: {response.status_code}")
    print(f"   Ответ: {response.json()}")
    
    # 2. Тест параметров в пути
    print("\n2. Параметры в пути:")
    response = requests.get(f"{BASE_URL}/user/Иван")
    print(f"   /user/Иван: {response.json()}")
    
    response = requests.get(f"{BASE_URL}/user/Мария/age/25")
    print(f"   /user/Мария/age/25: {response.json()}")
    
    # 3. Тест query параметров
    print("\n3. Query параметры:")
    response = requests.get(f"{BASE_URL}/search/?q=python&limit=5&sort=desc")
    print(f"   /search/?q=python&limit=5&sort=desc: {response.json()}")
    
    # 4. Тест POST запроса (Item)
    print("\n4. Создание товара:")
    new_item = {
        "name": "Ноутбук",
        "description": "Игровой ноутбук",
        "price": 75000,
        "tax": 7500,
        "in_stock": True
    }
    response = requests.post(f"{BASE_URL}/items/", json=new_item)
    print(f"   Статус: {response.status_code}")
    print(f"   Ответ: {response.json()}")
    
    # 5. Тест получения товаров
    print("\n5. Список товаров:")
    response = requests.get(f"{BASE_URL}/items/")
    print(f"   Всего товаров: {response.json()['count']}")
    
    # 6. Тест создания пользователя с валидацией
    print("\n6. Создание пользователя:")
    new_user = {
        "username": "john123",
        "email": "john@example.com",
        "age": 25
    }
    response = requests.post(f"{BASE_URL}/users/", json=new_user)
    print(f"   Статус: {response.status_code}")
    print(f"   Ответ: {response.json()}")
    
    # 7. Тест создания задачи (CRUD)
    print("\n7. CRUD операции с задачами:")
    new_task = {
        "title": "Изучить FastAPI",
        "description": "Выполнить все задания",
        "priority": 5
    }
    response = requests.post(f"{BASE_URL}/tasks/", json=new_task)
    print(f"   Создание задачи: {response.status_code}")
    
    if response.status_code == 201:
        task_data = response.json()
        task_id = task_data["id"]
        print(f"   ID задачи: {task_id}")
        
        # Получение задачи
        response = requests.get(f"{BASE_URL}/tasks/{task_id}")
        print(f"   Получение задачи: {response.status_code}")
        
        # Обновление задачи
        update_data = {"completed": True}
        response = requests.put(f"{BASE_URL}/tasks/{task_id}", json=update_data)
        print(f"   Обновление задачи: {response.status_code}")
        
        # Статистика
        response = requests.get(f"{BASE_URL}/tasks/stats/")
        print(f"   Статистика: {response.json()}")
    
    # 8. Тест обработки ошибок
    print("\n8. Обработка ошибок:")
    response = requests.get(f"{BASE_URL}/users/unknown_user")
    print(f"   Несуществующий пользователь: {response.status_code}")
    print(f"   Ошибка: {response.json()}")
    
    response = requests.get(f"{BASE_URL}/tasks/invalid-id")
    print(f"   Несуществующая задача: {response.status_code}")
    
    print("\n" + "=" * 50)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 50)

if __name__ == "__main__":
    test_all_endpoints()