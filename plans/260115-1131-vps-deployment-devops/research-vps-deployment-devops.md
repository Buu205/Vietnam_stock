# Viettel Cloud VPS Deployment + DevOps for Beginners

**Date:** 2026-01-15 | **Budget:** 300-500k VND/month | **Stack:** Next.js + FastAPI + PostgreSQL

---

## 1. Viettel Cloud VPS Specs & Setup

### Recommended Setup
- **OS:** Ubuntu 22.04 LTS (better docs, larger community)
- **Min Specs for 300-500k budget:**
  - 2 vCPU
  - 2-4 GB RAM
  - 50-100 GB SSD
  - 99.99% uptime SLA

### Viettel Cloud Benefits
- **Free DDoS protection** (unique in Vietnam)
- Tier 3 data centers (5 locations nationally)
- VXLAN virtual networks + VPN included
- Competitive pricing (contact direct for quotes)

### Initial Setup (First 30 mins)
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essentials
sudo apt install -y curl wget git htop
sudo apt install -y build-essential python3-dev

# Setup firewall
sudo ufw enable
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # HTTP
sudo ufw allow 443/tcp # HTTPS

# Create deploy user (non-root)
sudo useradd -m -s /bin/bash deployer
sudo visudo  # Add: deployer ALL=(ALL) NOPASSWD: /bin/systemctl
```

---

## 2. Docker + Docker Compose Deployment

### Architecture (Recommended)
```yaml
├── Next.js (port 3000)  → Nginx reverse proxy (port 80/443)
├── FastAPI (port 8000)  → Nginx reverse proxy
└── PostgreSQL (port 5432, internal only)
```

### docker-compose.yml Template
```yaml
version: '3.9'
services:
  nextjs:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        NEXT_PUBLIC_API_URL: https://api.yourdomain.com
    ports:
      - "3000:3000"
    environment:
      NODE_ENV: production
    restart: unless-stopped

  fastapi:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://user:pass@postgres:5432/appdb
      ENVIRONMENT: production
    depends_on:
      - postgres
    restart: unless-stopped

  postgres:
    image: postgres:16-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_USER: dbuser
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: appdb
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
      - ./letsencrypt:/etc/letsencrypt:ro
    depends_on:
      - nextjs
      - fastapi
    restart: unless-stopped

volumes:
  postgres_data:
```

### Production Next.js Dockerfile (Multi-stage)
```dockerfile
# Stage 1: Builder
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Runtime (much smaller!)
FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
EXPOSE 3000
CMD ["node", "server.js"]
```

**Key Benefits:** Standalone output = 40-60% smaller runtime images

---

## 3. Nginx + SSL Setup

### Nginx Configuration (nginx.conf)
```nginx
upstream nextjs {
    server nextjs:3000;
}

upstream fastapi {
    server fastapi:8000;
}

# Redirect HTTP → HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS for Next.js
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://nextjs;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}

# HTTPS for FastAPI
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://fastapi;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### SSL Certificate Setup (Let's Encrypt + Certbot)
```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get certificates (stop Docker first)
sudo docker-compose down

# For main domain
sudo certbot certonly --webroot -w /var/www/certbot \
  -d yourdomain.com -d www.yourdomain.com \
  -d api.yourdomain.com \
  --email your@email.com --agree-tos

# Auto-renewal (runs daily, retries every 12h)
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Restart Docker
sudo docker-compose up -d
```

**Certificates expire in 90 days.** Certbot auto-renewal is standard practice.

---

## 4. Domain + DNS Setup

### Vietnamese Registrars (Recommended)
- **VinaHost** - VNNIC certified, good support
- **Instra** - ICANN accredited
- **Asia Registry** - Regional provider

### DNS Configuration Steps
1. Register domain at registrar (e.g., yourdomain.vn)
2. Point A record to your VPS IP:
   ```
   yourdomain.vn     A  203.123.45.67
   www                CNAME yourdomain.vn
   api                A  203.123.45.67
   ```
3. Enable DNSSEC + Registry Lock for security
4. Wait 24h for propagation (check: `nslookup yourdomain.vn`)

---

## 5. CI/CD with GitHub Actions (Beginners)

### Setup SSH Keys (Once)
```bash
# On VPS
ssh-keygen -t ed25519 -f /home/deployer/.ssh/id_deploy -N ""
cat /home/deployer/.ssh/id_deploy.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# Copy private key to GitHub Secrets
cat /home/deployer/.ssh/id_deploy
```

### GitHub Secrets (Settings → Secrets)
- `DEPLOY_HOST` = 203.123.45.67
- `DEPLOY_USER` = deployer
- `DEPLOY_KEY` = (private key from above)

### Workflow File (.github/workflows/deploy.yml)
```yaml
name: Deploy to VPS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Deploy via SSH
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.DEPLOY_HOST }}
          username: ${{ secrets.DEPLOY_USER }}
          key: ${{ secrets.DEPLOY_KEY }}
          script: |
            cd ~/app
            git pull origin main
            docker-compose pull
            docker-compose up -d
            docker-compose exec -T fastapi alembic upgrade head
            echo "✅ Deployment complete"
```

### Deployment Script (~/app/deploy.sh)
```bash
#!/bin/bash
set -e

cd /home/deployer/app

echo "Pulling latest code..."
git pull origin main

echo "Building containers..."
docker-compose build --no-cache

echo "Starting services..."
docker-compose up -d

echo "Running migrations..."
docker-compose exec -T fastapi alembic upgrade head

echo "✅ Deployment successful at $(date)"
```

---

## 6. Quick Reference: First-Time Checklist

- [ ] VPS provisioned (Ubuntu 22.04, 2+ vCPU, 2+ GB RAM)
- [ ] SSH key added to VPS
- [ ] Docker + Docker Compose installed
- [ ] App code cloned to ~/app
- [ ] docker-compose.yml configured
- [ ] Nginx config created
- [ ] Domain registered + DNS pointed
- [ ] Let's Encrypt certificates obtained
- [ ] GitHub secrets configured
- [ ] First deploy successful
- [ ] Monitor: `docker-compose logs -f`

---

## Unresolved Questions

1. Viettel Cloud exact pricing for 300-500k budget (must contact direct)
2. PostgreSQL managed service vs container trade-offs for your data size
3. Backup strategy (automated snapshots, S3 replication)
4. Monitoring/alerting setup (Prometheus, Grafana, or 3rd party)

---

## Sources

- [Viettel Cloud VPS](https://viettelcloud.vn/)
- [Docker Compose Next.js FastAPI PostgreSQL Guide](https://www.travisluong.com/how-to-develop-a-full-stack-next-js-fastapi-postgresql-app-using-docker/)
- [FastAPI Docker Deployment](https://fastapi.tiangolo.com/deployment/docker/)
- [Next.js Docker Images 2026](https://thelinuxcode.com/nextjs-docker-images-how-i-build-predictable-fast-deployments-in-2026/)
- [Nginx + Let's Encrypt Setup](https://ryanschiang.com/nextjs-ssl-tutorial)
- [GitHub Actions SSH Deploy Guide](https://dev.to/miangame/how-to-automate-a-deploy-in-a-vps-with-github-actions-via-ssh-101e)
- [Appleboy SSH Action](https://github.com/appleboy/ssh-action)
- [Vietnamese Domain Registration](https://vinahost.vn/en/cheap-domain-registration-vietnam/)
- [VNNIC Registry](https://vnnic.vn/en/domain/regulations?lang=en)
