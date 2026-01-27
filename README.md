# LLMOps 

Each commit is divided into various sub section that is fundamentally important for LLMOps

### Commit 1 — [d0654ca](https://github.com/divyanshagrawal-gif/LLMOps/commit/d0654ca3a85b598ebe6fbddb6d7ba75538f3a59b) : LLMOps Gemini Gateway
### Commit 2 : Prompt Ops + Caching




## LLMOps Gemini Gateway ( Commit 1 )

A production-ready LLM Gateway service that provides a clean abstraction layer over Google's Gemini API, following core LLMOps patterns used in production.

### 🎯 Goal

By the end of this commit we will have:

✅ A production-style FastAPI service  
✅ Clean Gemini abstraction layer  
✅ Config-driven model setup  
✅ Ready for Docker & cloud scale  

### 🏗️ Architecture

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

### 🚀 Quick Start

#### Prerequisites
- Python 3.11+
- Google Gemini API key

#### Local Development

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

#### Docker

1. **Build and run:**
```bash
docker-compose up --build
```

The service will be available at `http://localhost:8001`

### 📡 API Endpoints

#### Health Check
```bash
GET /health
```

#### Chat (Non-streaming)
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

#### Chat Stream
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

### 🏛️ Project Structure

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

### 🔧 Features

- **Request ID tracking** - Every request gets a unique ID for tracing
- **Structured logging** - Production-ready logging with request context
- **Error handling** - Graceful error handling with proper logging
- **CORS enabled** - Ready for frontend integration
- **Streaming support** - Real-time streaming responses
- **Config management** - Environment-based configuration

### 📝 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Your Google Gemini API key |
| `DEFAULT_MODEL` | Yes | Default model name (e.g., `gemini-pro`) |

### 🧪 Testing

Test streaming with curl:
```bash
curl -N -X POST http://127.0.0.1:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Count to 10", "max_tokens": 100}'
```



## Prompt Ops + Caching 
By the end of this commit , you will have:

✅ Prompts as versioned artifacts (YAML)
✅ Prompt registry + loader
✅ Prompt switching without redeploy
✅ L1 + L2 caching (in-memory + Redis)
✅ Cache hit metrics

This directly addresses cost, reliability, and control.

PART A — PROMPT OPS (Non-Negotiable)
1️⃣ Prompt Design Philosophy (Important)

In production:
Prompts are code
Prompts change more often than models
Prompt rollback must be instant

So:
❌ No inline prompts
❌ No f-strings in handlers
✅ External YAML + versioning

Prompt Registry Structure

this folder:

app/prompts/
  summarizer/
    v1.yaml
    v2.yaml
  
Prompt Loader (Core Infra)
app/services/prompt_loader.py
✔️ Decoupled
✔️ Git-versionable
✔️ Model-agnostic


Use Prompt Registry in API

Update your endpoint logic.
app/api/chat.py (add new endpoint)
🚨 No redeploy needed to change prompt content.


PART B — CACHING (Token = 💸)

Caching Strategy
What we cache
Final rendered prompt
Model + temperature

Cache key
hash(prompt + model + temperature)

6️⃣ Add Redis (L2 Cache)
Update docker-compose.yml:

Cache Service
app/services/cache.py

Cache-Aware LLM Call
Update Gemini call logic:
app/services/llm_service.py (new)

Log Cache Hits
Add to logging:
logger.info(
    "cache_lookup",
    extra={
        "extra": {
            "request_id": request_id,
            "cache_hit": cache_hit
        }
    }
)