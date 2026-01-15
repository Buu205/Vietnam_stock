# Phase 5: Deployment

**Duration:** Week 19-20 (2 weeks)
**Priority:** P1 - Go Live
**Status:** Pending
**Prerequisites:** Phase 4 complete (all pages working locally)

---

## Context Links

- [Main Plan](../plan.md)
- [VPS Deployment Research](../research/researcher-vps-deployment-devops.md)
- [Phase 4: Feature Implementation](./phase-04-feature-implementation.md)

---

## Overview

This phase deploys the application to Viettel Cloud VPS with Docker, Nginx, and SSL. By the end, you'll have a production app accessible at your custom domain.

**Goals:**
- Docker containerization
- Viettel Cloud VPS setup
- Nginx reverse proxy with SSL
- CI/CD with GitHub Actions

---

## Key Insights from Research

1. **Docker Compose** - Orchestrate Next.js + FastAPI + PostgreSQL
2. **Multi-stage builds** - Smaller Docker images
3. **Let's Encrypt** - Free SSL certificates
4. **GitHub Actions** - Auto-deploy on push to main

---

## Architecture: Production Setup

```
INTERNET
    |
    | DNS: yourdomain.com → VPS_IP
    v
+------------------------------------------+
|              VIETTEL CLOUD VPS            |
|              Ubuntu 22.04 LTS             |
+------------------------------------------+
|                                          |
|  +------------------------------------+  |
|  |           NGINX                    |  |
|  |   - SSL termination                |  |
|  |   - Reverse proxy                  |  |
|  |   - Static file caching            |  |
|  +------------------------------------+  |
|       |                    |             |
|       v                    v             |
|  +----------+        +----------+        |
|  | Next.js  |        | FastAPI  |        |
|  | :3000    |        | :8000    |        |
|  +----------+        +----------+        |
|                           |              |
|                           v              |
|                    +------------+        |
|                    | PostgreSQL |        |
|                    | :5432      |        |
|                    +------------+        |
|                                          |
+------------------------------------------+
```

---

## Implementation Steps

### Week 19: Docker & Local Testing

#### Step 5.1: Create Dockerfiles

- [ ] **Backend Dockerfile**
  ```dockerfile
  # backend/Dockerfile
  FROM python:3.13-slim

  WORKDIR /app

  # Install dependencies
  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt

  # Copy application
  COPY . .

  # Create non-root user
  RUN useradd -m appuser && chown -R appuser:appuser /app
  USER appuser

  EXPOSE 8000

  CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
  ```

- [ ] **Frontend Dockerfile (multi-stage)**
  ```dockerfile
  # frontend/Dockerfile
  # Stage 1: Build
  FROM node:20-alpine AS builder

  WORKDIR /app

  # Install dependencies
  COPY package*.json ./
  RUN npm ci

  # Build application
  COPY . .

  # Set API URL for build
  ARG NEXT_PUBLIC_API_URL
  ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

  RUN npm run build

  # Stage 2: Production
  FROM node:20-alpine AS runner

  WORKDIR /app

  ENV NODE_ENV=production

  # Create non-root user
  RUN addgroup --system --gid 1001 nodejs
  RUN adduser --system --uid 1001 nextjs

  # Copy built files
  COPY --from=builder /app/public ./public
  COPY --from=builder /app/.next/standalone ./
  COPY --from=builder /app/.next/static ./.next/static

  USER nextjs

  EXPOSE 3000

  CMD ["node", "server.js"]
  ```

- [ ] **Update next.config.js for standalone**
  ```javascript
  // frontend/next.config.js
  /** @type {import('next').NextConfig} */
  const nextConfig = {
    output: 'standalone',
  }

  module.exports = nextConfig
  ```

#### Step 5.2: Create Docker Compose

- [ ] **Production docker-compose.yml**
  ```yaml
  # docker-compose.yml (project root)
  version: '3.9'

  services:
    frontend:
      build:
        context: ./frontend
        dockerfile: Dockerfile
        args:
          NEXT_PUBLIC_API_URL: ${NEXT_PUBLIC_API_URL:-http://localhost:8000}
      ports:
        - "3000:3000"
      environment:
        NODE_ENV: production
      depends_on:
        - backend
      restart: unless-stopped

    backend:
      build:
        context: ./backend
        dockerfile: Dockerfile
      ports:
        - "8000:8000"
      environment:
        DATABASE_URL: postgresql://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD:-postgres}@postgres:5432/${POSTGRES_DB:-vietnam_dashboard}
        SECRET_KEY: ${SECRET_KEY:-change-me-in-production}
        DATA_ROOT: /data
      volumes:
        - ./DATA:/data:ro  # Mount DATA directory read-only
      depends_on:
        postgres:
          condition: service_healthy
      restart: unless-stopped

    postgres:
      image: postgres:16-alpine
      environment:
        POSTGRES_USER: ${POSTGRES_USER:-postgres}
        POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres}
        POSTGRES_DB: ${POSTGRES_DB:-vietnam_dashboard}
      volumes:
        - postgres_data:/var/lib/postgresql/data
      healthcheck:
        test: ["CMD-SHELL", "pg_isready -U postgres"]
        interval: 5s
        timeout: 5s
        retries: 5
      restart: unless-stopped

    nginx:
      image: nginx:alpine
      ports:
        - "80:80"
        - "443:443"
      volumes:
        - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
        - ./nginx/ssl:/etc/nginx/ssl:ro
        - ./certbot/www:/var/www/certbot:ro
        - ./certbot/conf:/etc/letsencrypt:ro
      depends_on:
        - frontend
        - backend
      restart: unless-stopped

  volumes:
    postgres_data:
  ```

#### Step 5.3: Create Nginx Configuration

- [ ] **Create nginx directory**
  ```bash
  mkdir -p nginx
  ```

- [ ] **Create nginx.conf**
  ```nginx
  # nginx/nginx.conf
  events {
      worker_connections 1024;
  }

  http {
      include /etc/nginx/mime.types;
      default_type application/octet-stream;

      # Logging
      access_log /var/log/nginx/access.log;
      error_log /var/log/nginx/error.log;

      # Gzip compression
      gzip on;
      gzip_types text/plain text/css application/json application/javascript text/xml;

      # Upstream servers
      upstream frontend {
          server frontend:3000;
      }

      upstream backend {
          server backend:8000;
      }

      # HTTP - Redirect to HTTPS
      server {
          listen 80;
          server_name yourdomain.com www.yourdomain.com;

          # Let's Encrypt challenge
          location /.well-known/acme-challenge/ {
              root /var/www/certbot;
          }

          # Redirect all other traffic to HTTPS
          location / {
              return 301 https://$server_name$request_uri;
          }
      }

      # HTTPS - Main site
      server {
          listen 443 ssl http2;
          server_name yourdomain.com www.yourdomain.com;

          # SSL certificates
          ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
          ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

          # SSL settings
          ssl_protocols TLSv1.2 TLSv1.3;
          ssl_ciphers HIGH:!aNULL:!MD5;
          ssl_prefer_server_ciphers on;

          # API routes
          location /api/ {
              proxy_pass http://backend;
              proxy_http_version 1.1;
              proxy_set_header Host $host;
              proxy_set_header X-Real-IP $remote_addr;
              proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
              proxy_set_header X-Forwarded-Proto $scheme;
          }

          # Auth routes
          location /auth/ {
              proxy_pass http://backend;
              proxy_http_version 1.1;
              proxy_set_header Host $host;
              proxy_set_header X-Real-IP $remote_addr;
              proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
              proxy_set_header X-Forwarded-Proto $scheme;
          }

          # Frontend
          location / {
              proxy_pass http://frontend;
              proxy_http_version 1.1;
              proxy_set_header Upgrade $http_upgrade;
              proxy_set_header Connection "upgrade";
              proxy_set_header Host $host;
              proxy_set_header X-Real-IP $remote_addr;
              proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
              proxy_set_header X-Forwarded-Proto $scheme;
          }
      }
  }
  ```

#### Step 5.4: Test Locally with Docker

- [ ] **Build and run containers**
  ```bash
  # Create .env file
  cat > .env << EOF
  POSTGRES_USER=postgres
  POSTGRES_PASSWORD=secure_password_here
  POSTGRES_DB=vietnam_dashboard
  SECRET_KEY=your_random_secret_key_here
  NEXT_PUBLIC_API_URL=http://localhost:8000
  EOF

  # Build images
  docker-compose build

  # Start services (without nginx for local testing)
  docker-compose up -d frontend backend postgres

  # Check logs
  docker-compose logs -f

  # Test endpoints
  curl http://localhost:8000/api/health
  curl http://localhost:3000
  ```

### Week 20: VPS Setup & Deployment

#### Step 5.5: Viettel Cloud VPS Setup

- [ ] **Create VPS instance**
  - Go to: https://viettelcloud.vn/
  - Choose Ubuntu 22.04 LTS
  - Specs: 2 vCPU, 2-4 GB RAM, 50 GB SSD
  - Note your VPS IP address

- [ ] **SSH into VPS**
  ```bash
  ssh root@YOUR_VPS_IP
  ```

- [ ] **Initial server setup**
  ```bash
  # Update system
  apt update && apt upgrade -y

  # Install essentials
  apt install -y curl wget git htop

  # Setup firewall
  ufw enable
  ufw allow 22/tcp   # SSH
  ufw allow 80/tcp   # HTTP
  ufw allow 443/tcp  # HTTPS

  # Create deploy user
  useradd -m -s /bin/bash deployer
  usermod -aG sudo deployer

  # Set password
  passwd deployer

  # Switch to deployer
  su - deployer
  ```

- [ ] **Install Docker**
  ```bash
  # Install Docker
  curl -fsSL https://get.docker.com -o get-docker.sh
  sudo sh get-docker.sh

  # Add deployer to docker group
  sudo usermod -aG docker deployer

  # Install Docker Compose
  sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  sudo chmod +x /usr/local/bin/docker-compose

  # Verify
  docker --version
  docker-compose --version
  ```

#### Step 5.6: Domain & DNS Setup

- [ ] **Register domain** (if not already done)
  - VinaHost, Instra, or international registrar
  - Cost: ~150k VND/year for .com

- [ ] **Configure DNS records**
  ```
  Type    Name    Value
  A       @       YOUR_VPS_IP
  A       www     YOUR_VPS_IP
  A       api     YOUR_VPS_IP
  ```

- [ ] **Wait for DNS propagation** (up to 24 hours)
  ```bash
  # Check DNS
  nslookup yourdomain.com
  ```

#### Step 5.7: Deploy Application

- [ ] **Clone repository to VPS**
  ```bash
  cd ~
  git clone https://github.com/yourusername/vietnam-dashboard-web.git app
  cd app
  ```

- [ ] **Create production .env**
  ```bash
  cat > .env << EOF
  POSTGRES_USER=postgres
  POSTGRES_PASSWORD=$(openssl rand -base64 32)
  POSTGRES_DB=vietnam_dashboard
  SECRET_KEY=$(openssl rand -base64 32)
  NEXT_PUBLIC_API_URL=https://yourdomain.com
  EOF
  ```

- [ ] **Copy DATA directory** (if not in repo)
  ```bash
  # From your local machine
  scp -r DATA deployer@YOUR_VPS_IP:~/app/
  ```

- [ ] **Start without SSL first**
  ```bash
  # Start backend services
  docker-compose up -d frontend backend postgres

  # Verify services are running
  docker-compose ps
  docker-compose logs backend
  ```

#### Step 5.8: SSL Certificate Setup

- [ ] **Install Certbot**
  ```bash
  sudo apt install -y certbot
  ```

- [ ] **Create webroot directory**
  ```bash
  mkdir -p certbot/www
  ```

- [ ] **Get SSL certificate**
  ```bash
  # Stop nginx if running
  docker-compose stop nginx

  # Get certificate
  sudo certbot certonly --standalone \
    -d yourdomain.com \
    -d www.yourdomain.com \
    --email your@email.com \
    --agree-tos \
    --non-interactive

  # Copy certificates to project
  sudo cp -rL /etc/letsencrypt certbot/conf
  sudo chown -R deployer:deployer certbot/
  ```

- [ ] **Update nginx.conf with your domain**
  Replace `yourdomain.com` with your actual domain in nginx/nginx.conf

- [ ] **Start nginx**
  ```bash
  docker-compose up -d nginx

  # Verify HTTPS works
  curl -I https://yourdomain.com
  ```

#### Step 5.9: Setup Auto-Renewal

- [ ] **Create renewal script**
  ```bash
  cat > ~/renew-certs.sh << 'EOF'
  #!/bin/bash
  cd ~/app
  docker-compose stop nginx
  certbot renew
  cp -rL /etc/letsencrypt certbot/conf
  docker-compose start nginx
  EOF

  chmod +x ~/renew-certs.sh
  ```

- [ ] **Add to crontab**
  ```bash
  # Run weekly
  crontab -e
  # Add line:
  0 3 * * 0 /home/deployer/renew-certs.sh >> /home/deployer/cert-renewal.log 2>&1
  ```

#### Step 5.10: Setup CI/CD with GitHub Actions

- [ ] **Add SSH key to VPS**
  ```bash
  # On VPS
  mkdir -p ~/.ssh
  ssh-keygen -t ed25519 -f ~/.ssh/deploy_key -N ""
  cat ~/.ssh/deploy_key.pub >> ~/.ssh/authorized_keys
  chmod 600 ~/.ssh/authorized_keys

  # Copy private key (to add to GitHub)
  cat ~/.ssh/deploy_key
  ```

- [ ] **Add GitHub Secrets**
  Go to GitHub repo → Settings → Secrets → Actions
  - `DEPLOY_HOST` = YOUR_VPS_IP
  - `DEPLOY_USER` = deployer
  - `DEPLOY_KEY` = (paste private key from above)

- [ ] **Create GitHub Actions workflow**
  ```yaml
  # .github/workflows/deploy.yml
  name: Deploy to VPS

  on:
    push:
      branches: [main]

  jobs:
    deploy:
      runs-on: ubuntu-latest

      steps:
        - uses: actions/checkout@v4

        - name: Deploy to VPS
          uses: appleboy/ssh-action@master
          with:
            host: ${{ secrets.DEPLOY_HOST }}
            username: ${{ secrets.DEPLOY_USER }}
            key: ${{ secrets.DEPLOY_KEY }}
            script: |
              cd ~/app
              git pull origin main
              docker-compose build
              docker-compose up -d
              echo "Deployment complete at $(date)"
  ```

---

## Success Criteria

### Infrastructure Working

- [ ] VPS accessible via SSH
- [ ] Docker containers running
- [ ] PostgreSQL database accessible
- [ ] DATA directory mounted

### SSL & Domain

- [ ] Domain resolves to VPS IP
- [ ] HTTPS working (padlock in browser)
- [ ] HTTP redirects to HTTPS
- [ ] Certificate auto-renewal scheduled

### Application Working

- [ ] Frontend loads at https://yourdomain.com
- [ ] API responds at https://yourdomain.com/api/health
- [ ] Authentication works
- [ ] All pages load data correctly

### CI/CD Working

- [ ] GitHub Actions deploy on push to main
- [ ] No manual deployment needed

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| DNS propagation delay | Medium | Wait 24h, use nslookup to check |
| SSL certificate issues | High | Use --standalone mode for initial cert |
| Docker build fails | Medium | Build locally first, then push |
| VPS out of memory | High | Monitor with htop, add swap |

---

## Troubleshooting Guide

### Common Issues

**Docker container won't start:**
```bash
docker-compose logs backend  # Check logs
docker-compose exec backend sh  # Shell into container
```

**SSL certificate error:**
```bash
# Check certificate files exist
ls -la certbot/conf/live/yourdomain.com/

# Check nginx config
docker-compose exec nginx nginx -t
```

**Database connection error:**
```bash
# Check postgres is running
docker-compose ps postgres

# Check connection from backend
docker-compose exec backend python -c "from app.database import engine; print(engine.execute('SELECT 1').scalar())"
```

---

## Data Update Strategy (Validated)

You chose **both** auto cron job AND manual trigger options.

### Option A: Auto Cron Job (Recommended for Daily)

- [ ] **Create data update script on VPS**
  ```bash
  # ~/app/scripts/update_data.sh
  #!/bin/bash
  set -e

  echo "Starting data update at $(date)"
  cd ~/app

  # Run the daily update pipeline inside backend container
  docker-compose exec -T backend python -c "
  import sys
  sys.path.insert(0, '/data')  # DATA directory mounted at /data
  from PROCESSORS.pipelines.run_all_daily_updates import main
  main()
  "

  echo "Data update completed at $(date)"
  ```

- [ ] **Schedule cron job**
  ```bash
  chmod +x ~/app/scripts/update_data.sh

  # Add to crontab - runs daily at 4:30 PM Vietnam time (after market closes at 3:00 PM)
  crontab -e
  # Add line:
  30 16 * * * /home/deployer/app/scripts/update_data.sh >> /home/deployer/logs/data_update.log 2>&1
  ```

### Option B: Manual Trigger (For Immediate Updates)

- [ ] **Create manual update API endpoint**
  ```python
  # backend/app/routes/admin.py
  from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
  from app.dependencies import get_current_user_from_cookie

  router = APIRouter(prefix="/api/admin", tags=["admin"])

  @router.post("/update-data")
  async def trigger_data_update(
      background_tasks: BackgroundTasks,
      user = Depends(get_current_user_from_cookie)
  ):
      """Manually trigger data update (admin only)."""
      if user.email != "admin@yourdomain.com":  # Simple admin check
          raise HTTPException(status_code=403, detail="Admin only")

      background_tasks.add_task(run_data_update)
      return {"message": "Data update started in background"}

  def run_data_update():
      """Background task for data update."""
      import subprocess
      subprocess.run(["/home/deployer/app/scripts/update_data.sh"], check=True)
  ```

- [ ] **Or use SSH to trigger manually**
  ```bash
  # From your local machine
  ssh deployer@YOUR_VPS_IP "cd ~/app && ./scripts/update_data.sh"
  ```

### Monitor Data Updates

- [ ] **Check logs**
  ```bash
  tail -f ~/logs/data_update.log
  ```

- [ ] **Verify data freshness**
  ```bash
  ls -la ~/app/DATA/processed/technical/basic_data.parquet
  ```

---

## Next Phase

After completing Phase 5, proceed to:
[Phase 6: Production](./phase-06-production.md)

---

*Phase created: 2026-01-15*
