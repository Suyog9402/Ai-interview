# Interview Assistant Backend

This backend provides authentication and user management for the Interview Assistant application. The LiveKit agent for interviews runs separately using `main.py`.

## Architecture

- **FastAPI Backend** (`app/`) - Handles authentication, signup, login, and user management
- **LiveKit Agent** (`main.py`) - Handles interview functionality with voice AI

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the backend directory:

```env
# Database
DATABASE_URL=postgresql://postgres@localhost:5432/interview_assistant

# Security
SECRET_KEY=your-secret-key-change-in-production

# CORS
ALLOWED_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]

# LiveKit (for interview functionality)
LIVEKIT_URL=wss://your-livekit-server.livekit.cloud
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret

# Azure OpenAI (for interview functionality)
AZURE_OPENAI_REALTIME_ENDPOINT=your_azure_endpoint
AZURE_OPENAI_REALTIME_API_KEY=your_azure_api_key
AZURE_OPENAI_REALTIME_API_VERSION=2024-02-15-preview
```

### 3. Run FastAPI Backend

```bash
python start_fastapi.py
```

The API will be available at `http://localhost:8000`

### 4. Run LiveKit Agent (for interviews)

```bash
python main.py start
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/signup` - Create new user account
- `POST /api/v1/auth/login` - Login user
- `POST /api/v1/auth/login-form` - OAuth2 form login

### User Management
- `GET /api/v1/users/me` - Get current user info
- `PUT /api/v1/users/me` - Update current user
- `DELETE /api/v1/users/me` - Delete current user

## Database

The application uses PostgreSQL as the default database. Make sure you have PostgreSQL installed and running, and that the database `interview_assistant` exists.

## Frontend Integration

The frontend is configured to connect to the FastAPI backend at `http://localhost:8000/api/v1`. Update the `NEXT_PUBLIC_API_URL` environment variable in the frontend if needed.

## Security Features

- Password hashing with bcrypt
- JWT token authentication
- CORS protection
- Input validation with Pydantic
- SQL injection protection with SQLAlchemy 