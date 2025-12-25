# Настройка автоматического деплоя

Этот документ описывает настройку CI/CD pipeline для автоматической сборки и деплоя приложения через GitHub Actions.

## Архитектура

Workflow состоит из двух джоб:

1. **build-and-push** - сборка Docker образа и публикация в GitHub Container Registry
2. **deploy** - подключение к серверу по SSH и развертывание нового образа

## Настройка GitHub Repository

### 1. Включить права на запись для Actions

Перейдите в настройки репозитория:

```
Settings → Actions → General → Workflow permissions
```

Выберите: **Read and write permissions**

Поставьте галочку: **Allow GitHub Actions to create and approve pull requests**

Нажмите **Save**.

### 2. Настроить секреты для SSH

Перейдите в секреты:

```
Settings → Secrets and variables → Actions → New repository secret
```

Добавьте следующие секреты:

| Имя секрета | Описание | Пример |
|-------------|----------|--------|
| `SSH_HOST` | IP адрес или домен сервера | `123.45.67.89` или `server.example.com` |
| `SSH_USER` | Имя пользователя для SSH | `ubuntu` или `root` |
| `SSH_PRIVATE_KEY` | Приватный SSH ключ | Содержимое файла `~/.ssh/id_rsa` |
| `SSH_PORT` | Порт SSH (обычно 22) | `22` |

### 3. Генерация SSH ключа (если нужно)

На вашем локальном компьютере:

```bash
ssh-keygen -t ed25519 -C "github-actions"
```

Скопируйте публичный ключ на сервер:

```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@server
```

Содержимое приватного ключа (`~/.ssh/id_ed25519`) добавьте в секрет `SSH_PRIVATE_KEY`.

## Настройка сервера

### 1. Установить Docker

На сервере выполните:

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER

# Перезагрузка сессии
newgrp docker
```

### 2. Проверить Docker

```bash
docker --version
docker ps
```

### 3. Открыть порт 8000

Если используется firewall (ufw):

```bash
sudo ufw allow 8000/tcp
sudo ufw status
```

## Как работает деплой

### Триггеры

Workflow запускается автоматически при:
- Push в ветку `main`
- Ручном запуске через GitHub UI (workflow_dispatch)

### Процесс build-and-push

1. Checkout кода из репозитория
2. Логин в GitHub Container Registry (ghcr.io)
3. Извлечение метаданных (теги, labels)
4. Сборка Docker образа
5. Push образа в GHCR с тегами:
   - `latest` (для main ветки)
   - `main-<sha>` (с хешем коммита)
   - `main` (имя ветки)

### Процесс deploy

1. Подключение к серверу по SSH
2. Логин в GitHub Container Registry на сервере
3. Остановка и удаление старого контейнера `time-server`
4. Скачивание нового образа
5. Запуск нового контейнера с параметрами:
   - Имя: `time-server`
   - Порт: `8000:8000`
   - Restart policy: `unless-stopped`
   - Переменные окружения: `HOST`, `PORT`, `DEBUG`
6. Очистка неиспользуемых образов

## Ручной запуск

Перейдите в:

```
Actions → Build and Deploy → Run workflow → Run workflow
```

## Проверка деплоя

После успешного деплоя проверьте работу приложения:

```bash
# На сервере
docker ps
docker logs time-server

# Проверка API
curl http://your-server:8000/
curl http://your-server:8000/time
curl http://your-server:8000/health
```

## Troubleshooting

### Ошибка "Permission denied" при build

**Проблема:** Недостаточно прав для публикации в GHCR.

**Решение:** Проверьте настройки Workflow permissions (шаг 1).

### Ошибка SSH подключения

**Проблема:** Не удается подключиться к серверу.

**Решение:**
- Проверьте правильность секретов `SSH_HOST`, `SSH_USER`, `SSH_PORT`
- Убедитесь что SSH ключ добавлен на сервер
- Проверьте что порт SSH открыт в firewall

### Ошибка "docker: command not found" на сервере

**Проблема:** Docker не установлен или пользователь не в группе docker.

**Решение:** Выполните установку Docker (см. раздел "Настройка сервера").

### Образ не скачивается с GHCR

**Проблема:** Ошибка авторизации при `docker pull`.

**Решение:**
- Проверьте что образ публичный или сервер авторизован
- Убедитесь что `GITHUB_TOKEN` корректно передается

### Контейнер не запускается

**Проблема:** Порт 8000 уже занят.

**Решение:**
```bash
# Проверить что использует порт
sudo lsof -i :8000
# Остановить процесс или изменить порт в workflow
```

## Настройка переменных окружения

Для изменения переменных окружения отредактируйте секцию `docker run` в `.github/workflows/deploy.yml`:

```yaml
docker run -d \
  --name time-server \
  --restart unless-stopped \
  -p 8000:8000 \
  -e HOST=0.0.0.0 \
  -e PORT=8000 \
  -e DEBUG=false \
  $IMAGE_FULL
```

## Откат к предыдущей версии

Если нужно откатиться к предыдущей версии:

```bash
# На сервере
docker stop time-server
docker rm time-server

# Найти нужный тег образа
docker images | grep time-server

# Запустить конкретную версию
docker run -d \
  --name time-server \
  --restart unless-stopped \
  -p 8000:8000 \
  ghcr.io/username/repo:main-abc1234
```

## Мониторинг

Просмотр логов на сервере:

```bash
# Последние логи
docker logs time-server

# Следить за логами в реальном времени
docker logs -f time-server

# Последние 100 строк
docker logs --tail 100 time-server
```

Проверка статуса:

```bash
docker ps -a | grep time-server
```

