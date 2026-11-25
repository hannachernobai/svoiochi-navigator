FROM python:3.10-slim

WORKDIR /app

# Копіюємо всі файли проєкту в контейнер
COPY . .

# Встановлюємо залежності
RUN pip install --no-cache-dir -r requirements.txt

# Відкриваємо порт
EXPOSE 8000

# Запускаємо сервер
CMD ["python", "server.py"]