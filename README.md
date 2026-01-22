# LLMOps 

Each commit is divided into various sub section that is fundamentally important for LLMOps

### Commit 1 : LLMOps Gemini Gateway
### Commit 2 : Prompt Ops + Caching




# LLMOps Gemini Gateway

A production-ready LLM Gateway service that provides a clean abstraction layer over Google's Gemini API, following core LLMOps patterns used in production.

## 🎯 Goal

By the end of this commit we will have:

✅ A production-style FastAPI service  
✅ Clean Gemini abstraction layer  
✅ Config-driven model setup  
✅ Ready for Docker & cloud scale  

## 🏗️ Architecture

You are building your own LLM API, not an app.

Instead of your app talking directly to Gemini:
```
Client → Gemini API
```

you introduce your gateway:
```
Client → Your LLM Service → Gemini
```

This gives you:
- **Vendor independence** - Switch models without changing client code
- **Centralized control** - Logging, rate limits, retries in one place
- **One consistent API** - No matter which model you use later

This is the core LLMOps pattern used in production.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Google Gemini API key

### Local Development

1. **Clone and setup:**
```bash
cd LLMOps
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment:**
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_api_key_here
DEFAULT_MODEL=gemini-pro
```

3. **Run the service:**
```bash
# From project root
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

### Docker

1. **Build and run:**
```bash
docker-compose up --build
```

The service will be available at `http://localhost:8001`

## 📡 API Endpoints

### Health Check
```bash
GET /health
```

### Chat (Non-streaming)
```bash
POST /chat
Content-Type: application/json

{
  "prompt": "Explain quantum computing",
  "temperature": 0.7,
  "max_tokens": 1024
}
```

**Response:**
```json
{
  "response": "Quantum computing is...",
  "model": "gemini-pro",
  "latency": 1.23
}
```

### Chat Stream
```bash
POST /chat/stream
Content-Type: application/json

{
  "prompt": "Write a story",
  "temperature": 0.7,
  "max_tokens": 500
}
```

Returns streaming text chunks in real-time.

## 🏛️ Project Structure

```
LLMOps/
├── app/
│   ├── api/           # FastAPI route handlers
│   ├── core/          # Config, logging
│   ├── schemas/       # Pydantic models
│   ├── services/      # Gemini client abstraction
│   └── main.py        # FastAPI app
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## 🔧 Features

- **Request ID tracking** - Every request gets a unique ID for tracing
- **Structured logging** - Production-ready logging with request context
- **Error handling** - Graceful error handling with proper logging
- **CORS enabled** - Ready for frontend integration
- **Streaming support** - Real-time streaming responses
- **Config management** - Environment-based configuration

## 📝 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Your Google Gemini API key |
| `DEFAULT_MODEL` | Yes | Default model name (e.g., `gemini-pro`) |

## 🧪 Testing

Test streaming with curl:
```bash
curl -N -X POST http://127.0.0.1:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Count to 10", "max_tokens": 100}'
```

