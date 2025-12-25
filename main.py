from fastapi import FastAPI
from datetime import datetime
import os
import uvicorn

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Добро пожаловать в Time Server API! Используйте /time для получения Tекущего времени."}


@app.get("/time")
def get_server_time():
    now = datetime.now()
    return {
        "server_time": now.isoformat(),
        "timestamp": now.timestamp(),
        "formatted_time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "timezone": now.astimezone().tzname()
    }


@app.get("/date")
def get_server_date():
    now = datetime.now()
    return {
        "date": now.date().isoformat(),
        "year": now.year,
        "month": now.month,
        "day": now.day,
        "weekday": now.strftime("%A"),
        "formatted_date": now.strftime("%d.%m.%Y")
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    # Получаем настройки из переменных окружения
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug
    )

