# Сервис аутентификации на FastAPI

Этот репозиторий содержит **микросервис аутентификации**. Ниже приводится описание *только* тех возможностей, которые непосредственно реализованы в исходных файлах:

* [`dependecies.py`](applications/auth/dependecies.py)
  ‑ зависимости для FastAPI (проверка токена, получение текущего пользователя, валидация учётных данных).
* [`schemas.py`](applications/auth/schemas.py)
  ‑ Pydantic‑схемы запросов/ответов.
* [`user_service.py`](applications/auth/user_service.py)
  ‑ бизнес‑логика CRUD по пользователю.
* [`utils.py`](applications/auth/utils.py)
  ‑ хэширование паролей, создание/проверка JWT.
* [`views.py`](applications/auth/views.py)
  ‑ HTTP‑роуты (`/auth/*`).

---

## 📦 Зависимости (из `import`‑ов)

| Пакет             | Назначение                       |
| ----------------- | -------------------------------- |
| **fastapi**       | Веб‑фреймворк                    |
| **starlette**     | Ответы/запросы ASGI              |
| **sqlalchemy**    | БД (асинхронный ORM)             |
| **pydantic**      | Схемы данных                     |
| **bcrypt**        | Хэширование паролей              |
| **jwt** (`PyJWT`) | Генерация и проверка JWT‑токенов |

---

## 🗄️ Pydantic‑схемы

```python
class UserBase:    # базовое представление пользователя
    fullname: str | None
    phone: str | None
    email: EmailStr

class UserCreate(UserBase):
    password1: str  # пароль (повторяется для проверки)
    password2: str

class User:        # расширенная схема (ответы API)
    id: int
    created_at: datetime | None
    updated_at: datetime | None
    # + поля из UserBase

class UserLogin:   # форма входа (не используется напрямую в роутерах)
    email: EmailStr
    password: str

class Token:
    access_token: str
    refresh_token: str | None = None  # только при /sign‑in
    token_type: str = "Bearer"
```

---

## 🔐 Логика JWT (из `utils.py`)

| Константа           | Значение     | Назначение                |
| ------------------- | ------------ | ------------------------- |
| `_ACCESS_LIFETIME`  | **1 минута** | Срок жизни access‑токена  |
| `_REFRESH_LIFETIME` | **7 дней**   | Срок жизни refresh‑токена |
| `_ACCESS_TYPE`      | "access"     | Маркер в payload          |
| `_REFRESH_TYPE`     | "refresh"    | Маркер в payload          |

Функции:

* `hash_password()`   — bcrypt‑хэширование.
* `verify_password()` — проверка пароля.
* `create_access_token(user)` / `create_refresh_token(user)` — создают токены с полями `sub` (email) и, для access, `id`.
* `decode_jwt(token)` — проверка и декодирование.

Ключ и алгоритм берутся из `core.conf.settings` (`settings.secret_key`, `settings.algorithm`).

---

## 🖥️ HTTP‑роуты (из `views.py`)

| Метод    | Путь            | Тело запроса                               | Ответ                                | Особенности                                                                                              |
| -------- | --------------- | ------------------------------------------ | ------------------------------------ | -------------------------------------------------------------------------------------------------------- |
| **POST** | `/auth/sign-up` | `UserCreate` (JSON)                        | `User`                               | Создаёт пользователя. Проверяет совпадение `password1/password2`.                                        |
| **POST** | `/auth/sign-in` | `username` + `password` (form‑url‑encoded) | `Token` (только `access_token`)      | *Ставит* cookie `refresh_token` (HttpOnly, Secure). В заголовке ответа `Authorization: Bearer <access>`. |
| **POST** | `/auth/refresh` | –                                          | `Token` (обновлённый `access_token`) | Берёт refresh‑токен из cookies, возвращает новый access. Заголовок `Authorization` обновляется.          |
| **POST** | `/auth/logout`  | –                                          | `{ "success": true }`                | Удаляет cookie `refresh_token`.                                                                          |
| **GET**  | `/auth/auth/me` | –                                          | `User`                               | Требуется заголовок `Authorization: Bearer <access>`.                                                    |

---

## 🔄 Диаграмма обмена (кратко)

1. **Регистрация** → access‑токен не выдаётся.
2. **Вход** → `access_token` (в теле + заголовке), `refresh_token` (cookie).
3. **Обновление токена** → новый `access_token`; refresh‑cookie не изменяется.
4. **Выход** → refresh‑cookie удаляется; access‑токен клиент просто забывает.

---

## 🗃️ Сервисы и зависимости

| Файл              | Ключевые функции / классы                                                            |
| ----------------- | ------------------------------------------------------------------------------------ |
| `dependecies.py`  | `validate_auth_user`, `get_current_user`, `get_current_user_for_refresh_from_cookie` |
| `user_service.py` | `UserAuthService.create()`, `UserAuthService.get_user()`                             |
| `utils.py`        | Хэширование, генерация/проверка JWT                                                  |

`validate_auth_user` проверяет:

* существует ли пользователь по email;
* флаг `is_active` модели пользователя;
* корректность пароля (`verify_password`).

При неудачной проверке поднимаются `HTTPException` со статусами 400/401/404.

---
