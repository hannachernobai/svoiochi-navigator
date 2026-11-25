import sqlite3
import pandas as pd
import json
import os


def build_database():
    os.makedirs("data", exist_ok=True)
    db_path = os.path.join("data", "transport.db")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Таблиця маршрутів з реального CSV
    if os.path.exists('haraktyrystyka_marshrutiv_2025-02-07.csv'):
        df_routes = pd.read_csv('haraktyrystyka_marshrutiv_2025-02-07.csv')
        df_routes.to_sql('routes', conn, if_exists='replace', index=False)

    # 2. Таблиця транспорту з реального CSV
    if os.path.exists('vehicles-2025-01-24 (2).csv'):
        df_vehicles = pd.read_csv('vehicles-2025-01-24 (2).csv')
        df_vehicles.to_sql('vehicles', conn, if_exists='replace', index=False)

    # 3. Таблиця спеціальних презентаційних сценаріїв (Банкова 4 -> ЦНАП)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS demo_routes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT,
            instruction TEXT
        )
    ''')

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

    conn.commit()
    conn.close()
    print("Успішно створено базу даних transport.db у папці data/")


if __name__ == "__main__":
    build_database()