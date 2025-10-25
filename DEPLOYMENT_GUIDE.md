# Project Samarth - Deployment Guide

## 🚀 Deployment Options

Project Samarth can be deployed on various platforms. This guide covers multiple deployment strategies from local to cloud platforms.

## 📋 Pre-deployment Checklist

- [ ] All dependencies are listed in `requirements.txt`
- [ ] Environment variables are configured
- [ ] Data files are present in the `data/` directory
- [ ] Application runs successfully locally
- [ ] Database migrations (if any) are ready

## 🔧 Local Production Deployment

### Using Gunicorn (Recommended for Linux/Mac)

1. **Install Gunicorn**
   ```bash
   pip install gunicorn
   ```

2. **Create Gunicorn Configuration**
   ```bash
   # Save as gunicorn.conf.py
   bind = "0.0.0.0:5000"
   workers = 4
   worker_class = "sync"
   worker_connections = 1000
   timeout = 30
   keepalive = 2
   max_requests = 1000
   max_requests_jitter = 100
   preload_app = True
   ```

3. **Run with Gunicorn**
   ```bash
   cd backend
   gunicorn --config gunicorn.conf.py main:app
   ```

### Using Waitress (Recommended for Windows)

1. **Install Waitress**
   ```bash
   pip install waitress
   ```

2. **Run with Waitress**
   ```bash
   cd backend
   waitress-serve --host=0.0.0.0 --port=5000 main:app
   ```

## ☁️ Cloud Platform Deployments

### 1. Heroku Deployment

#### Step 1: Prepare Heroku Files

Create `Procfile`:
```
web: cd backend && gunicorn main:app
```

Create `runtime.txt`:
```
python-3.9.18
```

Update `requirements.txt`:
```
Flask==2.3.3
Flask-CORS==4.0.0
pandas==2.1.1
numpy==1.24.3
requests==2.31.0
python-dotenv==1.0.0
gunicorn==21.2.0
```

#### Step 2: Deploy to Heroku
```bash
# Install Heroku CLI first
heroku login
heroku create project-samarth-app
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

### 2. Railway Deployment

#### Step 1: Create railway.json
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "cd backend && python main.py",
    "healthcheckPath": "/api/health"
  }
}
```

#### Step 2: Deploy
```bash
# Install Railway CLI
npm install -g @railway/cli
railway login
railway init
railway up
```

### 3. Render Deployment

#### Step 1: Create render.yaml
```yaml
services:
  - type: web
    name: project-samarth
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: cd backend && gunicorn main:app
    healthCheckPath: /api/health
```

### 4. DigitalOcean App Platform

#### Step 1: Create .do/app.yaml
```yaml
name: project-samarth
services:
- name: web
  source_dir: /
  github:
    repo: your-username/project-samarth
    branch: main
  run_command: cd backend && gunicorn main:app
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  http_port: 5000
  health_check:
    http_path: /api/health
```

## 🐳 Docker Deployment

### Step 1: Create Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash samarth
RUN chown -R samarth:samarth /app
USER samarth

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/api/health || exit 1

# Run application
CMD ["python", "backend/main.py"]
```

### Step 2: Create docker-compose.yml
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - FLASK_DEBUG=false
    volumes:
      - ./data:/app/data
      - ./backend/logs:/app/backend/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
    restart: unless-stopped
```

### Step 3: Deploy with Docker
```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## 🌐 Reverse Proxy Configuration (Nginx)

Create `nginx.conf`:
```nginx
events {
    worker_connections 1024;
}

http {
    upstream samarth_app {
        server web:5000;
    }

    server {
        listen 80;
        server_name your-domain.com;

        location / {
            proxy_pass http://samarth_app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /static {
            alias /app/frontend/static;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

## 🔐 Environment Configuration

Create `.env.production`:
```bash
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=false
SECRET_KEY=your-super-secret-production-key

# Cache Configuration
CACHE_DIR=/app/data/cache
CACHE_TIMEOUT=3600

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=/app/backend/logs/samarth.log

# Security
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

## 📊 Monitoring and Logging

### Step 1: Enhanced Logging Configuration
```python
# Add to backend/main.py
import logging
from logging.handlers import RotatingFileHandler
import os

if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/samarth.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Project Samarth startup')
```

### Step 2: Health Check Endpoint Enhancement
```python
@app.route('/api/health/detailed', methods=['GET'])
def detailed_health_check():
    """Detailed health check for monitoring"""
    try:
        # Check database connections
        dataset_count = len([d for category in data_handler.dataset_registry.values() 
                           for d in category.values()])
        
        # Check cache
        cache_size = len(data_handler.query_cache)
        
        # Check disk space
        import shutil
        disk_usage = shutil.disk_usage('.')
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '2.0.0',
            'datasets_available': dataset_count,
            'cache_size': cache_size,
            'disk_free_gb': disk_usage.free // (1024**3),
            'uptime': time.time() - start_time
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500
```

## 🚀 Quick Deploy Commands

### Option 1: Heroku (Fastest)
```bash
git init
git add .
git commit -m "Initial commit"
heroku create your-app-name
git push heroku main
heroku open
```

### Option 2: Docker (Most Flexible)
```bash
docker-compose up -d
echo "App running at http://localhost"
```

### Option 3: Railway (Simplest)
```bash
railway login
railway init
railway up
```

### Option 4: Local Production
```bash
pip install gunicorn
cd backend
gunicorn --bind 0.0.0.0:5000 main:app
```

## 📱 Mobile Optimization

The frontend is already mobile-responsive, but for better mobile experience:

1. **PWA Configuration** (Progressive Web App)
2. **Service Worker** for offline functionality
3. **App Manifest** for mobile installation

## 🔒 Security Considerations

1. **Environment Variables**: Never commit sensitive data
2. **HTTPS**: Use SSL certificates in production
3. **Rate Limiting**: Implement API rate limiting
4. **Input Validation**: Sanitize all user inputs
5. **CORS**: Configure proper CORS policies

## 📈 Scaling Considerations

1. **Horizontal Scaling**: Use load balancers
2. **Database**: Consider PostgreSQL for production
3. **Caching**: Redis for distributed caching
4. **CDN**: Use CDN for static assets
5. **Monitoring**: Implement APM tools

---

Choose the deployment option that best fits your needs. Heroku and Railway are great for quick deployments, while Docker provides maximum flexibility for production environments.