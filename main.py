from fastapi import FastAPI, HTTPException
from datetime import datetime
from zoneinfo import ZoneInfo, available_timezones
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


@app.get("/convert-timezone")
def convert_timezone(time: str, timezone: str):
    """
    Конвертирует время из UTC в указанный часовой пояс.
    
    Параметры:
    - time: время в формате "HH:MM" или "HH:MM:SS" (например "15:00")
    - timezone: часовой пояс (например "Asia/Irkutsk", "Europe/Moscow")
    
    Примеры часовых поясов:
    - Asia/Irkutsk (Иркутск, UTC+8)
    - Europe/Moscow (Москва, UTC+3)
    - Asia/Yekaterinburg (Екатеринбург, UTC+5)
    - Asia/Vladivostok (Владивосток, UTC+10)
    """
    try:
        # Парсим входное время
        time_formats = ["%H:%M", "%H:%M:%S"]
        parsed_time = None
        
        for fmt in time_formats:
            try:
                parsed_time = datetime.strptime(time, fmt).time()
                break
            except ValueError:
                continue
        
        if parsed_time is None:
            raise HTTPException(
                status_code=400, 
                detail="Неверный формат времени. Используйте HH:MM или HH:MM:SS (например '15:00')"
            )
        
        # Проверяем существование часового пояса
        if timezone not in available_timezones():
            raise HTTPException(
                status_code=400,
                detail=f"Неизвестный часовой пояс: {timezone}. Примеры: Asia/Irkutsk, Europe/Moscow"
            )
        
        # Создаем datetime с текущей датой и указанным временем в UTC
        today = datetime.now().date()
        utc_datetime = datetime.combine(today, parsed_time, tzinfo=ZoneInfo("UTC"))
        
        # Конвертируем в целевой часовой пояс
        target_datetime = utc_datetime.astimezone(ZoneInfo(timezone))
        
        return {
            "input_time_utc": time,
            "target_timezone": timezone,
            "converted_time": target_datetime.strftime("%H:%M:%S"),
            "converted_datetime": target_datetime.isoformat(),
            "date": target_datetime.date().isoformat(),
            "utc_offset": target_datetime.strftime("%z")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка конвертации: {str(e)}")


@app.get("/timezones")
def list_timezones(search: str = None):
    """
    Получить список доступных часовых поясов.
    
    Параметры:
    - search: фильтр для поиска (необязательно)
    """
    zones = sorted(available_timezones())
    
    if search:
        zones = [z for z in zones if search.lower() in z.lower()]
    
    return {
        "count": len(zones),
        "timezones": zones[:100]  # Ограничиваем вывод первыми 100
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

