# lab2_Dawam_A_K

**ИМЯ**: Давам Алгар Кабирул  
**ИСУ**: 408516  
**Группа**: N3346  
**Поток**: WebПрог_ТЗИ_N3 1.3  

# News API with Authentication

CRUD API для управления новостями, пользователями и комментариями с системой аутентификации и авторизации, построенный на FastAPI.

## 🚀 Функциональность

- ✅ **Регистрация и аутентификация** через email/пароль
- ✅ **OAuth авторизация** через GitHub
- ✅ **JWT токены** с refresh механизмом
- ✅ **Ролевая модель**: обычный пользователь, верифицированный автор, администратор
- ✅ **Создание новостей** только верифицированными пользователями
- ✅ **Комментирование новостей** любыми авторизованными пользователями
- ✅ **Управление пользователями** (администраторы)
- ✅ **Активные сессии** с отслеживанием user agent
- ✅ **Полноценное API** для всех сущностей с защитой прав доступа

## 🛠 Технологии

- Python 3.10+
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- JWT токены
- GitHub OAuth
- Argon2 для хеширования паролей

## 📥 Установка и запуск

### 1. Клонируйте репозиторий:
```bash
git clone https://github.com/itmo-webdev/lab2_Dawam_A_K.git
cd lab2_Dawam_A_K
```

### 2. Установите зависимости:
```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# или .venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 3. Настройте базу данных PostgreSQL:

Создайте базу данных и пользователя:
```sql
CREATE DATABASE news_db;
CREATE USER news_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE news_db TO news_user;
```

### 4. Настройте переменные окружения:
Создайте файл `.env` в корне проекта:
```env
DATABASE_URL=postgresql://news_user:password@localhost:5432/news_db
SECRET_KEY=your-super-secret-key-change-in-production-12345
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
```

### 5. Примените миграции:
```bash
alembic upgrade head
```

### 6. Запустите приложение:
```bash
uvicorn app.main:app --reload
```

API будет доступно по адресу: **http://localhost:8000**

Документация API: **http://localhost:8000/docs**

## 🔐 Настройка GitHub OAuth (опционально)

1. Перейдите в [GitHub Developer Settings](https://github.com/settings/developers)
2. Создайте новое OAuth App:
   - **Application name**: News API
   - **Homepage URL**: http://localhost:8000
   - **Authorization callback URL**: http://localhost:8000/auth/github/callback
3. Получите Client ID и Client Secret
4. Обновите значения в `.env` файле

## 📖 Примеры использования API

### 1. Регистрация пользователя

```bash
curl -X POST "http://localhost:8000/auth/register" \
-H "Content-Type: application/json" \
-d '{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123"
}'
```

**Ответ:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### 2. Вход в систему

```bash
curl -X POST "http://localhost:8000/auth/login" \
-H "Content-Type: application/json" \
-d '{
  "email": "john@example.com",
  "password": "password123"
}'
```

### 3. GitHub OAuth авторизация

Перейдите в браузере по адресу:
```
http://localhost:8000/auth/github
```

### 4. Получение информации о текущем пользователе

```bash
curl -X GET "http://localhost:8000/users/me" \
-H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 5. Попытка создания новости (без верификации)

```bash
curl -X POST "http://localhost:8000/news/" \
-H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
-H "Content-Type: application/json" \
-d '{
  "title": "Моя первая новость",
  "content": {"blocks": [{"type":"paragraph","text":"Текст новости"}]}
}'
```

**Ошибка (если пользователь не верифицирован):**
```json
{
  "detail": "User is not verified to create news"
}
```

### 6. Верификация пользователя как автора (требует админских прав)

Сначала сделайте пользователя администратором через БД:
```sql
UPDATE users SET is_admin = true WHERE email = 'admin@example.com';
```

Затем обновите пользователя:
```bash
curl -X PUT "http://localhost:8000/users/1" \
-H "Authorization: Bearer ADMIN_ACCESS_TOKEN" \
-H "Content-Type: application/json" \
-d '{
  "is_verified_author": true
}'
```

### 7. Успешное создание новости

```bash
curl -X POST "http://localhost:8000/news/" \
-H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
-H "Content-Type: application/json" \
-d '{
  "title": "Моя первая новость",
  "content": {"blocks": [{"type":"paragraph","text":"Текст новости"}]},
  "cover": "http://example.com/image.jpg"
}'
```

### 8. Создание комментария

```bash
curl -X POST "http://localhost:8000/comments/" \
-H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
-H "Content-Type: application/json" \
-d '{
  "text": "Отличная статья!",
  "news_id": 1
}'
```

### 9. Получение списка новостей

```bash
curl -X GET "http://localhost:8000/news/" \
-H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 10. Обновление новости (только автор или администратор)

```bash
curl -X PUT "http://localhost:8000/news/1" \
-H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
-H "Content-Type: application/json" \
-d '{
  "title": "Обновленный заголовок",
  "content": {"blocks": [{"type":"paragraph","text":"Обновленный текст"}]}
}'
```

### 11. Обновление комментария (только автор или администратор)

```bash
curl -X PUT "http://localhost:8000/comments/1" \
-H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
-H "Content-Type: application/json" \
-d '{
  "text": "Обновленный комментарий"
}'
```

### 12. Удаление новости

```bash
curl -X DELETE "http://localhost:8000/news/1" \
-H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 13. Удаление комментария

```bash
curl -X DELETE "http://localhost:8000/comments/1" \
-H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 14. Обновление access token

```bash
curl -X POST "http://localhost:8000/auth/refresh" \
-H "Content-Type: application/json" \
-d '{
  "refresh_token": "YOUR_REFRESH_TOKEN"
}'
```

### 15. Выход из системы

```bash
curl -X POST "http://localhost:8000/auth/logout" \
-H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
-H "Content-Type: application/json" \
-d '{
  "refresh_token": "YOUR_REFRESH_TOKEN"
}'
```

### 16. Просмотр активных сессий

```bash
curl -X GET "http://localhost:8000/auth/sessions" \
-H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 👥 Ролевая модель

### Обычный пользователь
- Регистрация и вход в систему
- Просмотр новостей и комментариев
- Создание комментариев
- Редактирование и удаление своих комментариев

### Верифицированный автор
- Все права обычного пользователя
- Создание новостей
- Редактирование и удаление своих новостей

### Администратор
- Все права верифицированного автора
- Просмотр списка всех пользователей
- Редактирование любых пользователей
- Назначение статуса верифицированного автора
- Удаление любых новостей и комментариев

## 🔧 Администрирование

### Создание администратора через базу данных:

```sql
-- Создайте пользователя обычным способом через API, затем выполните:
UPDATE users SET is_admin = true, is_verified_author = true WHERE email = 'admin@example.com';
```

### Просмотр всех пользователей (только для администраторов):

```bash
curl -X GET "http://localhost:8000/users/" \
-H "Authorization: Bearer ADMIN_ACCESS_TOKEN"
```

## 🐛 Поиск и устранение неисправностей

### Проблемы с базой данных:
```bash
# Проверка подключения к БД
psql -U news_user -d news_db -c "\dt"

# Сброс и пересоздание БД
alembic downgrade base
alembic upgrade head
```

### Проблемы с миграциями:
```bash
# Просмотр текущей миграции
alembic current

# Принудительное выполнение миграций
alembic upgrade head
```

### Проблемы с аутентификацией:
- Убедитесь, что SECRET_KEY в `.env` файле совпадает
- Проверьте срок действия токенов
- Убедитесь, что пользователь существует и пароль верный

## 📁 Структура проекта

```
lab2_Dawam_A_K/
├── app/
│ ├── main.py
│ ├── models.py
│ ├── schemas.py
│ ├── db.py
│ ├── dependencies.py
│ ├── crud.py
│ ├── auth.py
│ ├── config.py
│ ├── repositories/
│ │ ├── base.py
│ │ ├── sqlalchemy_repo.py
│ │ └── mongodb_repo.py
│ └── routers/
│ ├── users.py
│ ├── news.py
│ ├── comments.py
│ └── auth.py
├── alembic/
│ ├── versions/
│ └── env.py
├── requirements.txt
├── alembic.ini
├── .env
└── README.md
```

## 📄 Лицензия

Этот проект является учебной работой для ИТМО.
