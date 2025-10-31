# AutoPM Backend - Authentication & Integration System

Complete FastAPI backend with JWT authentication and OAuth2 integrations for GitHub and Jira.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install sqlalchemy uvicorn fastapi pydantic-settings python-jose passlib bcrypt cryptography httpx python-dotenv python-multipart
```

Or install from requirements.txt:

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

The `.env` file is already created with SQLite defaults. Update the OAuth credentials:

- **GitHub OAuth**: Get from https://github.com/settings/developers
- **Jira OAuth**: Get from https://developer.atlassian.com/console/myapps/

For production, generate secure keys:

```bash
# Generate JWT Secret
openssl rand -hex 32

# Generate Encryption Key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 3. Run the Application

```bash
uvicorn main:app --reload
```

The API will be available at: http://localhost:8000

- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📁 Project Structure

```
fastapi_backend/
├── models/              # Database models
│   ├── user.py         # User model with roles
│   ├── integration_token.py  # OAuth tokens (encrypted)
│   └── base.py         # SQLAlchemy base
├── routes/              # API endpoints
│   ├── auth_routes.py  # /auth/register, /auth/login, /auth/me
│   └── integration_routes.py  # /integrations/connect/*
├── services/            # Business logic
│   ├── auth_service.py      # Authentication logic
│   └── integration_service.py  # OAuth2 flows
├── utils/               # Utilities
│   ├── jwt_handler.py  # JWT token operations
│   ├── password.py     # Password hashing (bcrypt)
│   └── encryption.py   # Token encryption (Fernet)
├── config.py           # Configuration management
├── database.py         # Database setup (SQLite)
├── main.py            # FastAPI application
├── .env               # Environment variables
└── requirements.txt   # Python dependencies
```

## 🔐 API Endpoints

### Authentication

- **POST** `/auth/register` - Register new user
- **POST** `/auth/login` - Login and get JWT token
- **GET** `/auth/me` - Get current user info
- **GET** `/auth/verify` - Verify JWT token

### Integrations

- **GET** `/integrations/github/url` - Get GitHub OAuth URL
- **POST** `/integrations/connect/github` - Connect GitHub account
- **GET** `/integrations/jira/url` - Get Jira OAuth URL
- **POST** `/integrations/connect/jira` - Connect Jira account
- **DELETE** `/integrations/disconnect/{provider}` - Disconnect integration
- **GET** `/integrations/status` - Get all integration statuses
- **GET** `/integrations/list` - List connected integrations

## 👥 User Roles

- **admin** - Full system access
- **manager** - Team management access
- **member** - Basic access (default)

## 🗄️ Database

Using **SQLite** for simplicity:
- Database file: `autopm.db`
- Created automatically on first run
- No manual database setup required

To reset the database, simply delete `autopm.db` and restart the application.

## 🔒 Security Features

✅ JWT authentication with configurable expiration
✅ Bcrypt password hashing
✅ OAuth2 tokens encrypted at rest (Fernet)
✅ Role-based access control
✅ CORS configuration
✅ SQLite with SQLAlchemy ORM

## 📝 Example Usage

### 1. Register a User

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword",
    "full_name": "John Doe",
    "role": "member"
  }'
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=securepassword"
```

### 3. Access Protected Endpoint

```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🛠️ Development

The database tables are created automatically on startup. If you need to modify models:

1. Update the model in `models/`
2. Delete `autopm.db`
3. Restart the application

For production, consider using migrations with Alembic.

## 📦 Dependencies

- **FastAPI** - Modern web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **Pydantic** - Data validation
- **python-jose** - JWT implementation
- **passlib** - Password hashing
- **cryptography** - Token encryption
- **httpx** - Async HTTP client for OAuth

## 🌐 Frontend Integration

The backend expects OAuth callbacks at:
- GitHub: `http://localhost:5173/callback/github`
- Jira: `http://localhost:5173/callback/jira`

Update `CORS_ORIGINS` in `.env` to match your frontend URL.

## 📄 License

MIT License - Feel free to use in your projects!
