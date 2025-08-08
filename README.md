# Flower Management API - Docker Setup

A FastAPI application for merging flower images using OpenAI's DALL-E API.

## Quick Start

1. **Environment Setup**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env and add your OpenAI API key
   # OPEN_AI_API_KEY=your_actual_api_key_here
   ```

2. **Run the Application**
   ```bash
   # Build and start all services
   docker-compose up --build -d
   
   # View logs
   docker-compose logs -f
   ```

3. **Access the API**
   - **Main API**: http://localhost
   - **API Documentation**: http://localhost/docs
   - **Health Check**: http://localhost/health

## Services

### Core Services
- **app**: FastAPI application (internal port 8000)
- **nginx**: Reverse proxy and load balancer (port 80)
- **redis**: Caching layer for performance

### Optional Monitoring (use `--profile monitoring`)
- **prometheus**: Metrics collection (port 9090)
- **grafana**: Metrics visualization (port 3000)

## Usage Examples

### Basic Usage
```bash
# Start core services
docker-compose up -d

# Start with monitoring
docker-compose --profile monitoring up -d
```

### Development
```bash
# For development with live reload
docker-compose up --build

# View specific service logs
docker-compose logs -f app
docker-compose logs -f nginx
```

### Production
```bash
# Production deployment
docker-compose -f docker-compose.yml up -d --build
```

## API Endpoints

- `POST /flower-merge/upload` - Upload 4 flower images to create a bouquet
- `GET /flower-merge/health` - Service health check
- `GET /health` - Application health check
- `GET /docs` - Interactive API documentation

## Configuration

Key environment variables in `.env`:

- `OPEN_AI_API_KEY` - Your OpenAI API key (required)
- `OPEN_AI_MODEL` - OpenAI model to use (default: gpt-4o)
- `DEBUG` - Enable debug mode (default: false)
- `MAX_IMAGES_PER_REQUEST` - Maximum images per request (default: 4)
- `MAX_FILE_SIZE` - Maximum file size in bytes (default: 5MB)

## Troubleshooting

### Check Service Status
```bash
docker-compose ps
docker-compose logs app
```

### Restart Services
```bash
docker-compose restart
docker-compose down && docker-compose up -d
```

### Clean Rebuild
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

## Architecture

```
Internet → Nginx (Port 80) → FastAPI App (Port 8000) → OpenAI API
                 ↓
              Redis Cache
```

## Security Features

- Rate limiting (10 requests/second per IP)
- File size limits
- Content type validation
- Security headers
- Non-root container user

## Monitoring (Optional)

Access monitoring services:
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

Enable monitoring:
```bash
docker-compose --profile monitoring up -d
```

# .env: 

OPEN_AI_API_KEY=

OPEN_AI_MODEL=gpt-4o
OPEN_AI_CHAT_MODEL=gpt-3.5-turbo
MAX_IMAGES_PER_REQUEST=4
MAX_FILE_SIZE=10485760
DEBUG=True**