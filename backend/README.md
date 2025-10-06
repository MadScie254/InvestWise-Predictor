# InvestWise Backend API

FastAPI-based backend for the InvestWise Predictor platform - an AI-powered investment prediction platform for Kenyan markets.

## Installation

### Development Installation

```bash
# Clone the repository
git clone https://github.com/MadScie254/InvestWise-Predictor.git
cd InvestWise-Predictor/backend

# Install in development mode
pip install -e .[dev]
```

### Production Installation

```bash
pip install investwise-backend
```

## Quick Start

```python
import uvicorn
from app.main import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Package Structure

```
app/
├── __init__.py          # Package initialization
├── main.py              # FastAPI application
├── api/                 # API routes
│   ├── __init__.py
│   └── v1/              # API version 1
│       ├── __init__.py
│       └── endpoints/   # API endpoints
├── core/                # Core configuration
├── db/                  # Database models and session
├── crud/                # Database operations
├── schemas/             # Pydantic schemas
└── utils/               # Utility functions
```

## Features

- FastAPI with async/await support
- SQLAlchemy 2.0 with async PostgreSQL
- JWT authentication with bcrypt
- Redis rate limiting and caching
- Comprehensive input validation
- ML model integration
- Prometheus metrics
- Health checks

## Dependencies

- FastAPI 0.104+
- SQLAlchemy 2.0+
- Pydantic 2.5+
- PostgreSQL (via psycopg2-binary)
- Redis
- JWT authentication
- And more...

## License

MIT License - see LICENSE file for details.