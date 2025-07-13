# Hub2 Conversational Agent

A lightweight conversational agent for Hub2 fintech PSP-aggregator serving West African markets. This agent can handle transaction queries using OpenAI function calling with a clean, controlled approach.

## Features

- **Transaction Listing**: Get user transactions with optional date range filtering
- **Transaction Details**: Fetch detailed information about specific transactions
- **Function Calling**: Clean, controlled data access through explicit domain functions
- **Supabase Integration**: PostgreSQL backend with dummy transaction data
- **REST API**: FastAPI-based endpoints for easy integration

## Architecture

The agent follows a clean function-calling pattern:

1. **Domain Functions**: Explicit, typed methods for data access
2. **Orchestrator**: OpenAI function calling with controlled execution
3. **Database Layer**: Supabase PostgreSQL integration
4. **API Layer**: FastAPI REST endpoints

## Quick Start

### 1. Environment Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

### 2. Environment Variables

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
```

### 3. Database Setup

Run the database migration to create tables and seed dummy data:

```bash
python -m hub2_agent.db.migrate
```

### 4. Start the Server

```bash
uvicorn hub2_agent.main:app --reload
```

### 5. Test the Agent

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "message": "Show me my transactions from last week"
  }'
```

## API Endpoints

### POST /chat
Main conversational endpoint that accepts user messages and returns agent responses.

**Request:**
```json
{
  "user_id": "user_123",
  "message": "Show me my transactions from last week"
}
```

**Response:**
```json
{
  "response": "Here are your transactions from last week...",
  "function_calls": [
    {
      "function": "list_transactions",
      "arguments": {
        "user_id": "user_123",
        "start_date": "2024-01-15",
        "end_date": "2024-01-22"
      }
    }
  ]
}
```

### GET /health
Health check endpoint.

## Domain Functions

The agent can call these controlled functions:

### list_transactions(user_id: str, start_date: str = None, end_date: str = None)
Returns transactions for a user, optionally within a date range.

### transaction_details(txn_id: str)
Returns full details for a specific transaction.

## Development

### Project Structure

```
src/hub2_agent/
├── __init__.py
├── main.py              # FastAPI app
├── agent/
│   ├── __init__.py
│   ├── orchestrator.py  # Function calling logic
│   └── functions.py     # Domain functions
├── db/
│   ├── __init__.py
│   ├── client.py        # Supabase client
│   ├── models.py        # Pydantic models
│   └── migrate.py       # Database migration
└── api/
    ├── __init__.py
    ├── models.py        # API request/response models
    └── routes.py        # API endpoints
```

### Adding New Functions

1. Add the function to `agent/functions.py`
2. Update the function schema in `agent/orchestrator.py`
3. Test with the API

## Security

- All database queries are parameterized to prevent SQL injection
- User authentication should be implemented for production
- API keys are stored in environment variables
- Function calling provides controlled access to data

## License

Proprietary - Hub2 Internal Use Only 