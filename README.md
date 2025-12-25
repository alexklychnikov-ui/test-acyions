# Time Server API

Простой FastAPI бэкэнд для получения текущего времени сервера.

## Установка

1. Создайте виртуальное окружение:
```bash
python -m venv venv
```

2. Активируйте виртуальное окружение:
```bash
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Windows CMD
.\venv\Scripts\activate.bat
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Настройка

Скопируйте `env.example` в `.env` и настройте переменные окружения:

```bash
HOST=0.0.0.0
PORT=8000
DEBUG=False
```

## Запуск

```bash
python main.py
```

Или через uvicorn:
```bash
uvicorn main:app --reload
```

## API Endpoints

### `GET /`
Приветственное сообщение

**Ответ:**
```json
{
  "message": "Добро пожаловать в Time Server API! Используйте /time для получения Tекущего времени."
}
```

### `GET /time`
Получить текущее время сервера

**Ответ:**
```json
{
  "server_time": "2025-12-25T12:30:45.123456",
  "timestamp": 1735128645.123456,
  "formatted_time": "2025-12-25 12:30:45",
  "timezone": "RTZ 2 (зима)"
}
```

### `GET /health`
Проверка состояния сервера

**Ответ:**
```json
{
  "status": "ok",
  "timestamp": "2025-12-25T12:30:45.123456"
}
```

## Документация API

После запуска сервера документация доступна по адресам:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

