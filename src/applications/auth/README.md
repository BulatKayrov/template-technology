# Сервис аутентификации на FastAPI

Этот мини‑модуль реализует базовый JWT‑механизм аутентификации пользователей с помощью **FastAPI**, **SQLAlchemy**, **bcrypt** и **PyJWT**. Из коробки доступны:

* регистрация нового пользователя с двойным вводом пароля;
* вход по email/паролю с выдачей **access‑токена** (lifetime — 3 мин.);
* декодирование и валидация токена на защищённых маршрутах;
* получение профиля текущего пользователя;
* (для админов) просмотр и деактивация любых пользователей.

> **Папка/namespace:** `applications.auth`
> **Зависимости окружения:** см. `pyproject.toml` или `requirements.txt`.

---

## Структура модулей

| Файл                  | Назначение                                                                                                                     |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **`utils.py`**        | Хеширование и проверка паролей, генерация/декодирование JWT, константы `ACCESS_LIFETIME` (3 мин), `REFRESH_LIFETIME` (15 мин). |
| **`schemas.py`**      | Pydantic‑схемы `User*`, `Token` для запросов/ответов.                                                                          |
| **`user_service.py`** | Слой работы с БД: создание, выборка, обновление, деактивация пользователей. Наследует `BaseRepository`.                        |
| **`dependecies.py`**  | Reusable FastAPI `Depends`: валидация логина‑пароля, извлечение payload из JWT, получение текущего пользователя.               |
| **`views.py`**        | Роутер `/auth`. Эндпойнты: `sign‑up`, `sign‑in`, `sign‑out`, `auth/me`.                                                        |

---

## Быстрый запуск

```bash
# 1. Клонируем репозиторий и устанавливаем зависимости
$ git clone <repo-url> && cd fastapi-auth
$ pip install -r requirements.txt  # или poetry install

# 2. Экспортируем обязательные переменные окружения
$ export SECRET_KEY="super‑secret‑string"
$ export ALGORITHM="HS256"         # по умолчанию
$ export DATABASE_URL="postgresql+asyncpg://user:pass@localhost/db"

# 3. Запускаем приложение
$ uvicorn main:app --reload  # main.py должен создавать FastAPI() и подключать router
```

<details>
<summary>Пример раздела <code>settings</code></summary>

```python
# core/conf.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    secret_key: str
    algorithm: str = "HS256"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
```

</details>

---

## API‑справка

### Регистрация пользователя

```
POST /auth/sign-up
Content-Type: application/json
{
  "fullname": "Иван Петров",
  "phone": "+79991112233",
  "email": "ivan@example.com",
  "password1": "StrongP@ssw0rd",
  "password2": "StrongP@ssw0rd"
}
```

**Ответ 200**

```json
{
  "id": 1,
  "fullname": "Иван Петров",
  "phone": "+79991112233",
  "email": "ivan@example.com",
  "created_at": "2025-07-02T10:15:42.000Z",
  "updated_at": null
}
```

### Авторизация (login)

```
POST /auth/sign-in
Content-Type: application/x-www-form-urlencoded
username=ivan@example.com&password=StrongP@ssw0rd
```

**Ответ 200**

```json
{
  "access_token": "<JWT>",
  "token_type": "Bearer"
}
```

### Получение профиля текущего пользователя

```
GET /auth/auth/me
Authorization: Bearer <JWT>
```

**Ответ 200** — объект `User` без поля `created_at`.

### Выход (logout)

```
POST /auth/sign-out
```

> **NB:** Сейчас метод-заглушка (`pass`). Можно расширить (чёрный список токенов либо RT rotation).

---

## Алгоритм работы аутентификации

```mermaid
graph TD
    A[Регистрация /sign-up] -->|hash_password| B(Храним hash в БД)
    C[Логин /sign-in] --> D{validate_auth_user}
    D -->|Корректная пара email+pass| E(encode_jwt → access_token)
    E --> F[Клиент хранит и отправляет JWT]
    F --> G{get_current_user}
    G -->|decode_jwt| H(Извлекаем email ⇒ SELECT
User)
    H --> I[Возвращаем объект User]
```

1. **Регистрация**

   * `user_service.create` сверяет `password1` и `password2`.
   * Пароль хешируется `bcrypt` и сохраняется.
2. **Авторизация**

   * `validate_auth_user` валидирует существо­вание пользователя и проверяет пароль через `verify_password`.
   * При успехе в `views.login` генерируется **access‑токен** (`encode_jwt`), срок — 3 минуты, поля `sub` (email) и `id`.
3. **Доступ к защищённым маршрутам**

   * Клиент добавляет заголовок `Authorization: Bearer <token>`.
   * `get_current_user` декодирует токен (`decode_jwt`), ловит ошибки `ExpiredSignature`/`InvalidToken`.
   * По email извлекается пользователь; неактивным (`is_active=False`) доступ запрещён.

> **Расширение:** Добавьте refresh‑токены и механизмы отзыва (blacklist/rotate) при необходимости.

---

## Тестирование с помощью httpie

```bash
# signup
http POST :8000/auth/sign-up fullname="Иван" phone="+79991234567" \
     email=ivan@example.com password1=Secret1 password2=Secret1

# login
http -f POST :8000/auth/sign-in username=ivan@example.com password=Secret1
# сохраним токен
export TOKEN="<скопируйте access_token>"

# get profile
http GET :8000/auth/auth/me "Authorization: Bearer $TOKEN"
```

---

## Возможные улучшения

* **Refresh‑токен** + cookie‑based хранение.
* **Email подтверждение** при регистрации.
* **Блокировка аккаунта** после N неверных попыток.
* **RBAC** через FastAPI `Depends`.
* **OpenAPI Tags & Examples** для наглядности.

---

## Обзор функций модулей

### `utils.py`

| Функция                                                                             | Что делает                                                                                                   | Особенности                                                                 |
| ----------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------- |
| `hash_password(password)`                                                           | Хеширует строку пароля с помощью **bcrypt** и возвращает результат как `str`.                                | Соль генерируется автоматически. fileciteturn1file3                      |
| `verify_password(plain_password, hashed_password)`                                  | Проверяет соответствие пароля и хеша.                                                                        | Возвращает `bool`. fileciteturn1file3                                    |
| `encode_jwt(payload, secret_key=settings.secret_key, algorithm=settings.algorithm)` | Генерирует **access‑token**: копирует переданный payload, добавляет `exp=now+3м` и `iat`, подписывает PyJWT. | Срок действия задаётся константой `_ACCESS_LIFETIME`. fileciteturn1file3 |
| `decode_jwt(token, ...)`                                                            | Декодирует и валидирует токен, возвращает словарь payload.                                                   | Бросает исключения PyJWT при ошибках. fileciteturn1file3                 |

### `dependecies.py`

| Функция                                           | Что делает                                                                           | Особенности                                                                                             |
| ------------------------------------------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------- |
| `validate_auth_user(username, password, session)` | Проверяет существование пользователя и корректность пароля.                          | Находит пользователя, вызывает `verify_password`, генерирует HTTP ошибки 404/401. fileciteturn1file1 |
| `get_payload(token)`                              | Декодирует переданный JWT, отлавливая `ExpiredSignatureError` и `InvalidTokenError`. | Используется как `Depends` во всех защищённых эндпойнтах. fileciteturn1file1                         |
| `get_current_user(payload, session)`              | Извлекает email из payload, достаёт пользователя из БД, проверяет `is_active`.       | HTTP 400/404 при ошибках. fileciteturn1file1                                                         |

### `views.py`

| Эндпойнт                          | Что выполняет                                                                   | Внутренние вызовы                                          |
| --------------------------------- | ------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| `POST /auth/sign-in` (`login`)    | Принимает валидированного `user`, выпускает `access_token`, возвращает `Token`. | `validate_auth_user` → `encode_jwt`. fileciteturn1file2 |
| `POST /auth/sign-up` (`register`) | Создаёт нового пользователя.                                                    | `user_auth_service.create`. fileciteturn1file2          |
| `POST /auth/sign-out` (`logout`)  | Заглушка.                                                                       | — fileciteturn1file2                                    |
| `GET /auth/auth/me` (`profile`)   | Возвращает текущего пользователя без `created_at`.                              | `get_current_user`. fileciteturn1file2                  |

### `user_service.py` (`UserService`)

| Метод                            | Что делает                                                     | Особенности                                              |
| -------------------------------- | -------------------------------------------------------------- | -------------------------------------------------------- |
| `create(data, session)`          | Проверяет совпадение паролей, хеширует, создаёт запись `User`. | Коммит + refresh. fileciteturn1file0                  |
| `find_all(user, session)`        | Возвращает всех пользователей, если `user.is_admin=True`.      | Иначе 403. fileciteturn1file0                         |
| `delete(user, session)`          | Деактивирует пользователя (`is_active=False`).                 | «Мягкое» удаление. fileciteturn1file0                 |
| `update(user_in, data, session)` | Обновляет изменённые поля `User`.                              | Использует `model_dump`. fileciteturn1file0           |
| `get_user(email, session)`       | Получает пользователя по email.                                | Возвращает `None`, если не найден. fileciteturn1file0 |

---

## Пошаговый порядок выполнения

### 1. Регистрация (`/auth/sign‑up`)

1. **`views.register`** принимает тело `UserCreate`.
2. Вызывает **`UserService.create`**:
   2.1. Сравнивает `password1` и `password2`.
   2.2. Хеширует пароль через `utils.hash_password`.
   2.3. Создаёт объект `User`, коммитит и возвращает.
3. Клиент получает JSON с данными нового пользователя.

### 2. Авторизация (`/auth/sign‑in`)

1. Клиент отправляет `username`/`password` в `application/x-www-form-urlencoded`.
2. **`validate_auth_user`**
   2.1. Запрашивает пользователя через `UserService.get_user`.
   2.2. Проверяет пароль функцией `utils.verify_password`.
3. **`views.login`**
   3.1. Формирует payload `{'sub': email, 'id': id}`.
   3.2. Генерирует JWT через `utils.encode_jwt`.
   3.3. Возвращает `Token` с `access_token`.

### 3. Доступ к защищённому ресурсу (`Authorization: Bearer <JWT>`)

1. FastAPI извлекает токен через встроенную схему OAuth2.
2. **`get_payload`** декодирует и валидирует JWT (`utils.decode_jwt`).
3. **`get_current_user`**
   3.1. Получает email из payload.
   3.2. Достаёт пользователя из БД; убеждается, что `is_active=True`.
4. Роутер получает объект `User` и выполняет бизнес‑логику.

### 4. (опционально) Просмотр всех пользователей админом

1. Админ вызывает кастомный эндпойнт, где внутри обращение к **`UserService.find_all`**.
2. Метод проверяет `user.is_admin` и возвращает список пользователей или 403.

---

## Лицензия

MIT © 2025
