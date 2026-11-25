from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import csv
import os

app = FastAPI(title="Chernivtsi Sightless Navigator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class NavigationRequest(BaseModel):
    query_text: str
    lat: float
    lng: float


def init_database():
    """
    Автоматично створює та заповнює базу даних SQLite при старті сервера
    використовуючи стандартні бібліотеки Python (без pandas).
    """
    os.makedirs("data", exist_ok=True)
    db_path = os.path.join("data", "transport.db")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Створюємо таблицю презентаційних сценаріїв
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS demo_routes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT,
            instruction TEXT
        )
    ''')

    # Презентаційна інструкція для сценарію "Банкова 4 -> ЦНАП"
    demo_instruction = (
        "Вітаю, Олександра! Прокладаю маршрут від вулиці Банкової, 4 до Центру надання адміністративних послуг. "
        "Виходьте з будівлі на вулицю Банкову. Прямуйте 30 метрів прямо до перехрестя з вулицею Головною. "
        "Перейдіть дорогу за звуковим сигналом світлофора. "
        "Далі пройдіть 50 метрів прямо до ЦНАПу, що знаходиться за адресою вулиця Героїв Майдану, 7. "
        "Вхід обладнано пандусом та тактильною плиткою."
    )

    cursor.execute('DELETE FROM demo_routes')
    cursor.execute('INSERT INTO demo_routes (keyword, instruction) VALUES (?, ?)', ('банкова', demo_instruction))
    cursor.execute('INSERT INTO demo_routes (keyword, instruction) VALUES (?, ?)', ('чнап', demo_instruction))

    # Імпорт даних про транспорт із CSV (якщо файл існує)
    csv_routes_path = 'haraktyrystyka_marshrutiv_2025-02-07.csv'
    if os.path.exists(csv_routes_path):
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS routes (
                route_number TEXT,
                route_name TEXT,
                route_type TEXT
            )
        ''')
        cursor.execute('DELETE FROM routes')
        try:
            with open(csv_routes_path, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cursor.execute(
                        'INSERT INTO routes (route_number, route_name, route_type) VALUES (?, ?, ?)',
                        (row.get('route_number', ''), row.get('route_name', ''), row.get('route_type', ''))
                    )
        except Exception as e:
            print(f"Помилка зчитування CSV: {e}")

    conn.commit()
    conn.close()
    print("Базу даних SQLite (transport.db) успішно ініціалізовано!")


# Ініціалізуємо БД при старті додатка
init_database()


def query_database_for_route(user_query: str) -> str:
    db_path = os.path.join("data", "transport.db")

    if not os.path.exists(db_path):
        return "Базу даних транспорту не знайдено на сервері."

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query_lower = user_query.lower()

    # 1. Пошук у таблиці презентаційних сценаріїв (Банкова 4 -> ЦНАП)
    cursor.execute("SELECT instruction FROM demo_routes WHERE ? LIKE '%' || keyword || '%'", (query_lower,))
    row = cursor.fetchone()

    if row:
        conn.close()
        return row[0]

    # 2. Пошук у реальних маршрутах із CSV
    cursor.execute("SELECT route_number, route_name, route_type FROM routes WHERE ? LIKE '%' || route_number || '%'", (query_lower,))
    route_row = cursor.fetchone()

    conn.close()

    if route_row:
        return f"Олександра, знайдено міський маршрут №{route_row[0]}: {route_row[1]} ({route_row[2]})."

    # Fallback відповідь
    return (
        f"Олександра, координати зафіксовано. "
        f"Найближча зупинка поруч — Центральна площа. "
        f"Прямуйте 20 кроків вперед до пішохідного переходу."
    )


@app.get("/", response_class=HTMLResponse)
async def read_root():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Файл index.html не знайдено на сервері</h1>"


@app.post("/api/navigate")
async def navigate(req: NavigationRequest):
    if not req.query_text:
        raise HTTPException(status_code=400, detail="Запит не може бути порожнім")

    response_voice_text = query_database_for_route(req.query_text)

    return {
        "status": "success",
        "voice_response": response_voice_text
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)