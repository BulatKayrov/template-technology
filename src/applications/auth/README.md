# FastAPI Authentication Service

A lightweight authentication microservice built with **FastAPI** that provides JWT‑based authentication (access & refresh tokens), user registration, and profile management.

---

## ✨ Features

* **User registration & login** (email & password)
* **Secure password hashing** with *bcrypt*
* **Stateless JWT authentication**

  * Short‑lived **access** tokens
  * Long‑lived **refresh** tokens (HTTP‑only cookie)
* Token refresh & logout endpoints
* Role / status checks (active, admin)
* Fully async stack (FastAPI + SQLAlchemy 2)
* Auto‑generated OpenAPI & Swagger docs

---

## 📂 Project Structure

```
applications/
└── auth/
    ├── dependecies.py    # DI helpers & current‑user resolvers
    ├── schemas.py        # Pydantic DTOs
    ├── user_service.py   # CRUD & business logic
    ├── utils.py          # Hashing & JWT helpers
    └── views.py          # FastAPI router
core/
    └── database.py       # Async engine / session factory (not provided)
```

---

## ⚙️ Requirements

| Package              | Purpose             |
| -------------------- | ------------------- |
| **fastapi**          | Web framework       |
| **uvicorn**          | ASGI server         |
| **sqlalchemy**       | ORM (async)         |
| **pydantic**         | Data validation     |
| **bcrypt**           | Password hashing    |
| **pyjwt**            | JWT encode / decode |
| **python‑multipart** | Form parsing        |

> Python **3.11+** is recommended.

Install all dependencies:

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

The service relies on a few settings (see `core/conf.py`). Create a `.env` file:

```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/dbname
SECRET_KEY=your‑very‑strong‑secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1      # match utils._ACCESS_LIFETIME
REFRESH_TOKEN_EXPIRE_DAYS=7        # match utils._REFRESH_LIFETIME
```

---

## 🚀 Running Locally

```bash
uvicorn main:app --reload
```

Navigate to `http://127.0.0.1:8000/docs` for interactive Swagger UI.

---

## 🗺️ API Reference

### Auth Router (prefix `/auth`)

| Method                                            | Path         | Body                                | Description                                             |
| ------------------------------------------------- | ------------ | ----------------------------------- | ------------------------------------------------------- |
| **POST**                                          | `/sign-up`   | `UserCreate`                        | Register a new user                                     |
| **POST**                                          | `/sign-in`   | *form‑data* `username` + `password` | Login → returns `Token`; sets **refresh\_token** cookie |
| **POST**                                          | `/refresh`   | –                                   | Issue new **access\_token** using refresh cookie        |
| **POST**                                          | `/logout`    | –                                   | Delete refresh cookie                                   |
| **GET**                                           | `/auth/me`\* | –                                   | Get current user profile (                              |
| requires `Authorization: Bearer <access>` header) |              |                                     |                                                         |

> *Note: path is `/auth/auth/me` because of router prefix; adjust to your needs.*

#### Data Models

```jsonc
// UserCreate
{
  "fullname": "John Doe",
  "phone": "+39‑123‑456‑7890",
  "email": "john@example.com",
  "password1": "string",
  "password2": "string"
}

// Token
{
  "access_token": "<jwt>",
  "refresh_token": "<jwt>", // optional
  "token_type": "Bearer"
}
```

---

## 🖥️ Quick Start (cURL)

```bash
# Sign‑up\curl -X POST http://localhost:8000/auth/sign-up \
  -H "Content-Type: application/json" \
  -d '{"fullname":"Alice","email":"alice@example.com","password1":"pass","password2":"pass"}'

# Sign‑in (form encoded)
curl -X POST http://localhost:8000/auth/sign-in \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice@example.com&password=pass" -i

# Extract access; then:
curl http://localhost:8000/auth/auth/me \
  -H "Authorization: Bearer <access_token>"
```

---

## 🧪 Tests

```bash
pytest -q
```

*(Sample tests not included).*

---

## 🏗️ Roadmap

* Password reset & email verification
* OAuth (Google / GitHub)
* Dockerfile & docker‑compose
* RBAC / permissions
* Rate limiting

---

## 📄 License

This project is licensed under the MIT License – see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgements

Inspired by the official FastAPI security guide and community best practices.
