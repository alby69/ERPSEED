# ERPSEED - Low-Code ERP Platform

## Project Structure

This repository uses a multi-branch strategy:

| Branch | Description |
|--------|-------------|
| `main` | Docker deployment configuration |
| [erpseed/backend](https://github.com/alby69/ERPSEED/tree/erpseed/backend) | Backend-only ERPSEED Core |
| [erpseed/frontend](https://github.com/alby69/ERPSEED/tree/erpseed/frontend) | React frontend application |

## Quick Start with Docker

```bash
# Clone the repository
git clone https://github.com/alby69/ERPSEED.git
cd ERPSEED

# Start all services with Docker
docker-compose up -d

# Access the application
# Frontend: http://localhost:5173
# Backend API: http://localhost:5002
```

## Docker Services

- **db**: PostgreSQL 15
- **redis**: Redis 7
- **backend**: Flask API (builds from `erpseed/backend` branch)
- **frontend**: React/Vite (builds from `erpseed/frontend` branch)

## Customizing Build Branch

To use a different branch for backend or frontend, edit `docker-compose.yml`:

```yaml
args:
  - BRANCH=your-branch-name
```

## Development

To develop locally:

```bash
# Backend
git checkout erpseed/backend
# ... make changes ...

# Frontend  
git checkout erpseed/frontend
# ... make changes ...
```

## License

MIT License
