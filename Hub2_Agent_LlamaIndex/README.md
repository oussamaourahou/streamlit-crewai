# Hub2 LlamaIndex Conversational Agent

A lightweight conversational agent for Hub2 fintech platform using **LlamaIndex** with SQL database integration for natural language transaction queries.

## 🚀 Features

- **LlamaIndex ReAct Agent** - Advanced reasoning and action framework
- **Natural Language to SQL** - Convert user questions to SQL automatically  
- **Direct PostgreSQL Access** - Query Supabase database directly via SQL
- **Flexible Queries** - Handle complex, open-ended transaction questions
- **West African Context** - Optimized for Hub2's West African markets

## 📁 Project Structure

```
hub2_agent_llama/
├── __init__.py
├── main.py                    # FastAPI app
├── agent/
│   ├── __init__.py
│   └── llama_agent.py         # LlamaIndex ReAct Agent
├── db/
│   ├── __init__.py
│   ├── client.py              # Database connection
│   └── models.py              # Pydantic models
└── api/
    ├── __init__.py
    ├── models.py              # API models
    └── routes.py              # FastAPI routes
```

## 🛠 Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Configuration
Copy and configure your environment variables:
```bash
cp .env.example .env
```

Required variables:
```env
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key

# Supabase Configuration  
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_DB_PASSWORD=your-database-password
SUPABASE_DB_CONNECTION_STRING=postgresql://postgres.project:password@host:port/postgres
```

### 3. Test Connection
```bash
python debug.py
```

## 🎯 Usage

### Command Line Interface
```bash
# Interactive chat
python cli.py

# Quick test
python cli.py --test

# Specific user
python cli.py --user-id "your-user-id"
```

### FastAPI Server
```bash
# Start server
uvicorn hub2_agent_llama.main:app --reload

# Test endpoint
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user-123", "message": "Show me my recent transactions"}'
```

### Test Suite
```bash
python test_agent.py
```

## 💬 Example Queries

The agent can handle natural language queries like:

- "Show me all my transactions"
- "What are my failed transactions?"
- "How much have I spent this month?"
- "Show me transactions over 1000 XOF"
- "What's my average transaction amount?"
- "List transactions from merchant M123ABC"
- "Show me transactions from last week"

## 🔧 Technical Details

### LlamaIndex vs Function-Calling
- **Function-Calling:** Explicit Python functions for each query type
- **LlamaIndex:** LLM generates SQL queries automatically from natural language
- **Benefits:** More flexible, handles complex queries, adapts to schema changes

### Database Integration
- Uses SQLAlchemy for robust database connections
- Supports both Supabase HTTP API (fallback) and direct PostgreSQL access
- Connection pooling for better performance
- Automatic schema introspection

## 📊 Performance

- **Response Time:** ~2-5 seconds for complex queries
- **Accuracy:** High for transaction-related queries
- **Scalability:** Handles concurrent requests via FastAPI
- **Reliability:** Automatic fallback to HTTP API if SQL fails

## 🛡 Security

- Environment variables for sensitive data
- Input validation via Pydantic models
- SQL injection protection via parameterized queries
- User-specific data filtering

## 🌍 West African Optimization

- XOF currency formatting
- Local context awareness
- Culturally appropriate responses
- Hub2-specific terminology

---

**Built for Hub2's fintech ecosystem in West Africa** 🌍 