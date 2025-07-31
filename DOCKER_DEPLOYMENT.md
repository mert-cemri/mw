# Docker Deployment Guide

## Quick Start

### Prerequisites
- Docker Desktop installed and running
- OpenAI API key (optional, for real analysis mode)

### Deploy in 3 Steps

```bash
# 1. Clone the repository
git clone <repository-url>
cd mast-annotator-web

# 2. Set up environment (optional)
cp .env.example .env
# Edit .env if needed

# 3. Start the application
docker compose up -d
```

### Access the Application

Once running, access:
- 🎨 **Web Interface**: http://localhost:8501
- 📚 **API Documentation**: http://localhost:3000/docs
- ✅ **Health Check**: http://localhost:3000/health

## How to Use

### 1. Upload a Trace File
1. Open http://localhost:8501 in your browser
2. Click "Browse files" or drag and drop your trace file
3. Supported formats: JSON, JSONL, CSV, TXT, ZIP

### 2. View Analysis Results
- The system analyzes traces for 15 failure modes across 3 categories
- Results show as an interactive chart and downloadable report
- Each failure mode is marked as detected or not detected

### 3. Download Results
- **JSON**: Raw analysis data
- **Figure**: Publication-quality visualization
- **Report**: Human-readable summary

## Configuration

### Environment Variables

Create a `.env` file or export these variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | - | Your OpenAI API key (for production mode) |
| `MAST_FAKE_MODE` | `1` | `1` = demo mode (no API calls), `0` = real analysis |
| `MAST_MAX_FILE_MB` | `25` | Maximum file upload size in MB |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

### Running Modes

#### 🧪 Demo Mode (Default)
Perfect for testing - no API key needed:
```bash
docker compose up -d
```

#### 🚀 Production Mode
For real analysis with OpenAI:
```bash
export OPENAI_API_KEY="your-api-key-here"
export MAST_FAKE_MODE=0
docker compose up -d
```

## Common Commands

### Container Management
```bash
# View logs
docker compose logs -f

# Stop the application
docker compose down

# Restart the application
docker compose restart

# Update and rebuild
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Data Management
```bash
# Backup data
docker run --rm -v mast-data:/data -v $(pwd):/backup alpine \
  tar czf /backup/mast-backup-$(date +%Y%m%d).tar.gz -C /data .

# Restore data
docker run --rm -v mast-data:/data -v $(pwd):/backup alpine \
  tar xzf /backup/mast-backup-20240731.tar.gz -C /data

# Clean everything (⚠️ removes all data!)
docker compose down -v
```

## Troubleshooting

### Port Already in Use?

If you see "port already in use" errors:

1. **Check what's using the ports:**
   ```bash
   lsof -i :8501  # Streamlit port
   lsof -i :3000  # API port
   ```

2. **Change ports in `docker-compose.yml`:**
   ```yaml
   ports:
     - "3001:3000"  # API - change 3001 to any free port
     - "8502:9000"  # UI - change 8502 to any free port
   ```

### Container Won't Start?

1. **Check logs:**
   ```bash
   docker compose logs --tail=50
   ```

2. **Verify Docker is running:**
   ```bash
   docker ps
   ```

3. **Ensure clean state:**
   ```bash
   docker compose down
   docker compose up -d
   ```

### Can't Access the Web Interface?

1. **Verify container is healthy:**
   ```bash
   docker compose ps
   ```

2. **Test the connection:**
   ```bash
   curl http://localhost:3000/health
   ```

3. **Check browser:**
   - Clear cache or use incognito mode
   - Ensure you're using http:// not https://

### OpenAI API Errors?

1. **Verify your API key:**
   ```bash
   echo $OPENAI_API_KEY
   ```

2. **Test in demo mode first:**
   ```bash
   export MAST_FAKE_MODE=1
   docker compose restart
   ```

## Production Deployment Tips

### 1. Use a Reverse Proxy
```nginx
server {
    listen 80;
    server_name mast.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    location /api {
        proxy_pass http://localhost:3000;
    }
}
```

### 2. Set Resource Limits
Add to `docker-compose.yml`:
```yaml
services:
  mast-annotator:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

### 3. Enable HTTPS
Use Let's Encrypt with your reverse proxy for SSL/TLS.

### 4. Monitor the Application
- Set up log aggregation (e.g., ELK stack)
- Monitor container health
- Track API usage and response times

## Security Best Practices

- ⚠️ Never commit `.env` files or API keys to version control
- 🔒 Use Docker secrets for sensitive data in production
- 🔄 Regularly update base images and dependencies
- 👤 The container already runs as non-root user for security

## Need Help?

- Check the main [README.md](README.md) for application usage
- View [CLAUDE.md](../CLAUDE.md) for development guidance
- Report issues at the project repository