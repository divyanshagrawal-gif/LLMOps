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



## Prompt Ops + Caching (Commit 2)

By the end of this commit, we will have:

✅ Prompts as versioned artifacts (YAML)  
✅ Prompt registry + loader with variable substitution  
✅ Prompt switching without redeploy  
✅ Redis-based caching (L2 cache)  
✅ Cache-aware streaming and non-streaming responses  
✅ Cache hit metrics in responses and logs  

This directly addresses **cost** (reduce API calls), **reliability** (consistent responses), and **control** (prompt versioning).

---

### PART A — PROMPT OPS

#### 🎯 Prompt Design Philosophy

In production:
- **Prompts are code** - They need versioning, review, and rollback
- **Prompts change more often than models** - Business logic lives in prompts
- **Prompt rollback must be instant** - No redeploy needed

**Principles:**
- ❌ No inline prompts in code
- ❌ No f-strings in handlers
- ✅ External YAML files with versioning
- ✅ Git-tracked prompt changes

#### 📁 Prompt Registry Structure

Prompts are organized by name and version:

```
app/prompts/
  summarizer/
    v1.yaml
    v2.yaml
  [future prompts]/
    v1.yaml
```

**YAML Format:**
```yaml
name: summarizer
version: v1
system: |
  You are a concise summarizer.
user: |
  Summarize the following text clearly:

  {{text}}
```

Variables are substituted using `{{variable_name}}` syntax.

#### 🔧 Prompt Loader Implementation

**Location:** `app/services/prompt_loader.py`

**Features:**
- ✅ Decoupled from model providers
- ✅ Git-versionable (YAML files in repo)
- ✅ Model-agnostic (works with any LLM)
- ✅ Structured logging for load/render operations
- ✅ Error handling with detailed context

**Usage:**
```python
from app.services.prompt_loader import PromptLoader

loader = PromptLoader()

# Load prompt definition
prompt_def = loader.load(name="summarizer", version="v1")

# Render with variables
final_prompt = loader.render(
    prompt_def,
    {"text": "Your content here"}
)
```

#### 🚀 Using Prompts in API

**Example: `/summarize` endpoint**

```python
@router.post("/summarize")
def summarize(request: ChatRequest, req: Request):
    # Load prompt version (no redeploy needed to change)
    prompt_def = prompt_loader.load(
        name="summarizer",
        version="v1"  # Switch to "v2" to use new version
    )
    
    # Render with user input
    final_prompt = prompt_loader.render(
        prompt_def,
        {"text": request.prompt}
    )
    
    # Use cached LLM call
    result, cache_hit = generate_with_cache(...)
```

**Benefits:**
- 🚨 **No redeploy needed** - Change YAML file and restart service
- 📝 **Version control** - Track prompt changes in Git
- 🔄 **Easy rollback** - Switch version in code or config
- 🧪 **A/B testing** - Test different prompt versions

---

### PART B — CACHING (Token = 💸)

#### 🎯 Caching Strategy

**What we cache:**
- Final rendered prompt (after variable substitution)
- Model name
- Temperature parameter

**Cache Key:**
```
SHA256(prompt:model:temperature)
```

This ensures identical prompts with same parameters return cached results.

#### 🗄️ Redis Setup (L2 Cache)

**Docker Compose Configuration:**
```yaml
services:
  redis:
    image: redis:latest
    ports:
      - "6379:6379"
```

**Cache Service:** `app/services/cache.py`
- SHA256-based key generation
- JSON serialization for complex responses
- Configurable TTL (default: 3600 seconds / 1 hour)
- Redis connection with decode_responses enabled

#### 🔄 Cache-Aware LLM Service

**Location:** `app/services/llm_service.py`

**Implementation Details:**

1. **Non-Streaming Requests:**
   - Check cache before LLM call
   - Return cached response if found
   - Cache new responses after generation
   - Return `(result, cache_hit)` tuple

2. **Streaming Requests:**
   - **Cache Hit:** Simulate streaming by chunking cached text (50 chars/chunk)
   - **Cache Miss:** Stream from LLM while collecting chunks, cache after completion
   - Maintains streaming UX even for cached responses

**Function Signature:**
```python
def generate_with_cache(
    prompt: str,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    request_id: str = None,
    stream: bool = False
) -> tuple:
    # Returns (result/generator, cache_hit: bool)
```

#### 📊 Cache Metrics

**Response Metadata:**
- All responses include `cache_hit: bool` field
- Streaming responses indicate cache status in metadata

**Structured Logging:**
```python
logger.info(
    "cache_hit",  # or "cache_miss"
    extra={
        "extra": {
            "request_id": request_id,
            "prompt": prompt,
            "model": model,
            "temperature": temperature
        }
    }
)
```

**Example Response:**
```json
{
  "response": "Cached response text...",
  "model": "gemini-pro",
  "latency": 0.001,
  "cache_hit": true
}
```

#### 🎯 API Integration

**Non-Streaming:**
```python
@router.post("/chat")
def chat(request: ChatRequest, req: Request):
    result, cache_hit = generate_with_cache(
        prompt=request.prompt,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        request_id=req.state.request_id,
        stream=False
    )
    return ChatResponse(..., cache_hit=cache_hit)
```

**Streaming:**
```python
@router.post("/chat/stream")
def chat_stream(request: ChatRequest, req: Request):
    def generate():
        generator, cache_hit = generate_with_cache(
            prompt=request.prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            request_id=req.state.request_id,
            stream=True
        )
        for chunk in generator:
            yield chunk
    return StreamingResponse(generate(), ...)
```

#### 💡 Benefits

- **Cost Reduction:** Cache hits avoid expensive LLM API calls
- **Performance:** Sub-millisecond response times for cached requests
- **Consistency:** Same prompt = same response (deterministic)
- **Streaming Support:** Cached responses still stream for better UX
- **Observability:** Cache hit/miss metrics in logs and responses

#### Note
- **No Deploy:** No deploy in PromptOps here means that the overhead for deployment becomes less, you don't need to deploy the entire app again for the new prompt effect to take place. In further commits we will see how we can reduce this overhead further. 

### PART C - Prompt Version Switching + A/B Testing

#### Why ? 
In real systems:
- Prompt quality changes weekly
- You can’t redeploy for every tweak
- You must compare prompts on real traffic

So we need:
- Config-driven prompt selection
- Controlled rollout
- Measurable impact

### Extending to environment variables 
We add the SUMMARIZER_PROMPT_VERSION in the environment variable to track the version of summarizer prompt version, so now we can directly call `export SUMMARIZER_PROMPT_VERSION = v3` so the prompt version will change and the start the container, no redploy happened. 

### In case of production apps
- Adding the SUMMARIZER_PROMPT_VERSION variable in environment variable solves the issue of redeployment because it was before specified in the code.
- It helps remove the redployment phase for the changes to take effect you need to restart the service to changes to take effects which have no downtime, for changes to take effect reduced from hours to minutes. 

#### Prompt A/B Testing (Controlled)
Strategy
- Split traffic (e.g. 50/50)
- Assign one prompt per request
- Stickiness via request_id


