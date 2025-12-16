# Skyvern Development Setup

This repository has been set up for development with the following environment:

## 🚀 Quick Start

### 1. Initial Setup (one-time)
```bash
./dev-setup.sh
```

### 2. Start Services
```bash
# Start both API server and UI
./dev-start.sh

# Or start specific services
./dev-start.sh server  # API only
./dev-start.sh ui       # UI only
```

### 3. Stop Services
```bash
./dev-stop.sh
```

## 🌐 Access URLs

- **API Server**: http://localhost:28743
- **Web UI**: http://localhost:28742  
- **API Documentation**: http://localhost:28743/docs
- **Interactive API Docs**: http://localhost:28743/redoc

## 📋 Prerequisites

- ✅ Python 3.12.8 (installed)
- ✅ Node.js 20.19.1 (installed)
- ✅ Docker & Docker Compose (installed)
- ✅ PostgreSQL database (via Docker)

## 🔧 Environment Configuration

The `.env` file contains configuration for:
- Database connection (PostgreSQL via Docker)
- LLM providers (OpenAI, Anthropic, Azure, etc.)
- Browser settings
- API keys and secrets

**Note**: You'll need to configure at least one LLM provider in `.env` to use Skyvern.

## 🏗️ Development Architecture

- **Backend**: Python FastAPI application
- **Frontend**: Node.js + React + Vite
- **Database**: PostgreSQL 14 (Docker)
- **Browser Automation**: Playwright

## 📦 Directory Structure

```
skyvern/
├── skyvern/                 # Python backend
├── skyvern-frontend/        # React frontend  
├── skyvern-ts/             # TypeScript client
├── alembic/                # Database migrations
├── docker-compose.yml        # Docker configuration
├── .env                    # Environment variables
├── dev-setup.sh           # Initial setup script
├── dev-start.sh           # Start services script
└── dev-stop.sh            # Stop services script
```

## 🧪 Testing

The development environment is ready for:
- Backend API development
- Frontend UI development
- Database schema changes
- Browser automation testing
- LLM integration testing

## 🐛 Troubleshooting

1. **Database connection issues**: Ensure PostgreSQL container is running
   ```bash
   docker ps | grep skyvern-postgres-1
   ```

2. **Port conflicts**: Check if ports 28743 and 28742 are available
   ```bash
   lsof -i :28743,28742
   ```

3. **Dependency issues**: Reinstall Python dependencies
   ```bash
   source .venv/bin/activate
   pip install -e .
   ```

## 📚 Additional Resources

- [Skyvern Documentation](https://docs.skyvern.com)
- [API Reference](http://localhost:28743/docs)
- [GitHub Repository](https://github.com/Skyvern-AI/skyvern)
