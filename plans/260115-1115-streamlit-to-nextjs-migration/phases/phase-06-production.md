# Phase 6: Production Operations

**Duration:** Week 21+ (Ongoing)
**Priority:** P2 - Maintenance & Growth
**Status:** Pending
**Prerequisites:** Phase 5 complete (app deployed)

---

## Context Links

- [Main Plan](../plan.md)
- [Phase 5: Deployment](./phase-05-deployment.md)

---

## Overview

This phase covers ongoing production operations: monitoring, backups, performance optimization, and future enhancements. These are tasks you'll do periodically after launch.

**Goals:**
- Monitoring and alerting
- Backup and recovery
- Performance optimization
- User feedback collection
- Future feature planning

---

## Production Checklist

### Daily Tasks

- [ ] **Check application health**
  ```bash
  # On VPS
  docker-compose ps
  curl -s https://yourdomain.com/api/health | jq
  ```

- [ ] **Check disk space**
  ```bash
  df -h
  ```

- [ ] **Check logs for errors**
  ```bash
  docker-compose logs --since 24h backend | grep -i error
  docker-compose logs --since 24h frontend | grep -i error
  ```

### Weekly Tasks

- [ ] **Review access logs**
  ```bash
  docker-compose exec nginx cat /var/log/nginx/access.log | tail -100
  ```

- [ ] **Check certificate expiry**
  ```bash
  openssl s_client -connect yourdomain.com:443 -servername yourdomain.com 2>/dev/null | openssl x509 -noout -dates
  ```

- [ ] **Check for system updates**
  ```bash
  sudo apt update
  sudo apt list --upgradable
  ```

### Monthly Tasks

- [ ] **Update dependencies** (carefully, in dev first)
- [ ] **Review and clean up logs**
- [ ] **Check database size**
  ```bash
  docker-compose exec postgres psql -U postgres -c "SELECT pg_size_pretty(pg_database_size('vietnam_dashboard'));"
  ```

---

## Monitoring Setup

### Option A: Simple Monitoring (Free)

- [ ] **Create health check script**
  ```bash
  # ~/health-check.sh
  #!/bin/bash

  HEALTH=$(curl -s -o /dev/null -w "%{http_code}" https://yourdomain.com/api/health)

  if [ "$HEALTH" != "200" ]; then
      echo "$(date): Health check FAILED (status: $HEALTH)" >> ~/health.log
      # Optional: send notification
      # curl -X POST "https://api.telegram.org/bot<TOKEN>/sendMessage" \
      #   -d "chat_id=<CHAT_ID>&text=Health check failed!"
  else
      echo "$(date): OK" >> ~/health.log
  fi
  ```

- [ ] **Schedule health check**
  ```bash
  crontab -e
  # Run every 5 minutes
  */5 * * * * /home/deployer/health-check.sh
  ```

### Option B: Uptime Monitoring Services (Free Tier)

- [ ] **UptimeRobot** (free, 50 monitors)
  - https://uptimerobot.com/
  - Create HTTP monitor for your domain

- [ ] **Better Uptime** (free tier available)
  - https://betteruptime.com/

---

## Backup Strategy

### Database Backup

- [ ] **Create backup script**
  ```bash
  # ~/backup-db.sh
  #!/bin/bash

  BACKUP_DIR=~/backups
  DATE=$(date +%Y%m%d_%H%M%S)
  FILENAME="vietnam_dashboard_$DATE.sql.gz"

  mkdir -p $BACKUP_DIR

  docker-compose exec -T postgres pg_dump -U postgres vietnam_dashboard | gzip > $BACKUP_DIR/$FILENAME

  # Keep only last 7 days
  find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

  echo "Backup created: $FILENAME"
  ```

- [ ] **Schedule daily backups**
  ```bash
  crontab -e
  # Run at 2 AM daily
  0 2 * * * /home/deployer/backup-db.sh >> /home/deployer/backup.log 2>&1
  ```

### Restore from Backup

```bash
# Restore database
gunzip < backup_file.sql.gz | docker-compose exec -T postgres psql -U postgres vietnam_dashboard
```

---

## Performance Optimization

### Backend Optimizations

- [ ] **Add response caching**
  ```python
  # In FastAPI routes
  from fastapi_cache import FastAPICache
  from fastapi_cache.decorator import cache

  @router.get("/api/tickers/")
  @cache(expire=300)  # Cache for 5 minutes
  def list_tickers():
      ...
  ```

- [ ] **Optimize database queries**
  - Add indexes on frequently queried columns
  - Use pagination for large datasets

### Frontend Optimizations

- [ ] **Enable Next.js caching**
  ```typescript
  // In data fetching
  export const revalidate = 3600  // Revalidate every hour
  ```

- [ ] **Optimize images**
  - Use Next.js Image component
  - Lazy load below-fold content

### Docker Optimizations

- [ ] **Limit container resources**
  ```yaml
  # docker-compose.yml
  services:
    backend:
      deploy:
        resources:
          limits:
            cpus: '0.5'
            memory: 512M
  ```

---

## Security Checklist

### Regular Security Tasks

- [ ] **Update system packages**
  ```bash
  sudo apt update && sudo apt upgrade -y
  ```

- [ ] **Review Docker images for vulnerabilities**
  ```bash
  docker scan frontend:latest
  docker scan backend:latest
  ```

- [ ] **Check for exposed secrets**
  - Review .env files
  - Ensure no secrets in git history

- [ ] **Review access logs for suspicious activity**
  ```bash
  # Look for unusual patterns
  docker-compose exec nginx cat /var/log/nginx/access.log | \
    awk '{print $1}' | sort | uniq -c | sort -rn | head -20
  ```

### Security Hardening

- [ ] **Enable fail2ban** (optional)
  ```bash
  sudo apt install fail2ban
  sudo systemctl enable fail2ban
  ```

- [ ] **Setup SSH key-only auth**
  ```bash
  # In /etc/ssh/sshd_config
  PasswordAuthentication no
  ```

---

## User Management

### Adding New Users

```python
# Via API or script
from app.database import SessionLocal
from app.models.db_models import User
from app.dependencies import get_password_hash

db = SessionLocal()
user = User(
    email="newuser@example.com",
    hashed_password=get_password_hash("secure_password"),
    full_name="New User"
)
db.add(user)
db.commit()
```

### User Analytics (Optional)

- [ ] **Track active users**
  ```python
  # Add to auth endpoints
  import logging
  logger = logging.getLogger("user_activity")

  @router.post("/auth/login")
  def login(...):
      logger.info(f"Login: {user.email}")
      ...
  ```

---

## Future Enhancements

### Phase 6A: Data Migration to PostgreSQL (Optional)

If Parquet files become a bottleneck:

1. Create PostgreSQL tables for financial data
2. Write migration script from Parquet to PostgreSQL
3. Update services to use PostgreSQL instead of Parquet
4. Set up daily data sync

### Phase 6B: Real-time Updates (Optional)

For live stock prices:

1. Add WebSocket support to FastAPI
2. Create WebSocket client in Next.js
3. Connect to real-time data source (vnstock or exchange API)

### Phase 6C: Community Features (Optional)

For user engagement:

1. User profiles and preferences
2. Watchlists and alerts
3. Comments and discussion
4. Sharing and social features

### Phase 6D: Mobile App (Optional)

For mobile-first experience:

1. React Native app using same API
2. Push notifications for alerts
3. Offline mode with local storage

---

## Troubleshooting Reference

### Application Not Starting

```bash
# Check container status
docker-compose ps

# Check logs
docker-compose logs backend
docker-compose logs frontend

# Restart services
docker-compose restart

# Full restart
docker-compose down && docker-compose up -d
```

### Database Issues

```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Connect to database
docker-compose exec postgres psql -U postgres vietnam_dashboard

# Check database size
\l+
```

### SSL Issues

```bash
# Check certificate
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com

# Renew certificate manually
sudo certbot renew --force-renewal
```

### High Memory Usage

```bash
# Check memory usage
htop

# Check Docker container usage
docker stats

# Add swap if needed
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## Success Metrics

Track these metrics monthly:

- [ ] **Uptime**: Target > 99%
- [ ] **Response time**: Target < 2 seconds
- [ ] **Active users**: Track growth
- [ ] **Error rate**: Target < 1%
- [ ] **Database size**: Monitor growth

---

## Congratulations!

If you've completed all phases, you have:

1. Learned Python, web development, and DevOps fundamentals
2. Built a production-ready full-stack application
3. Deployed to a VPS with Docker, Nginx, and SSL
4. Set up CI/CD for automatic deployments
5. Implemented monitoring and backup strategies

**Total Time Investment:** ~20 weeks (5 months)

**Skills Gained:**
- Python + FastAPI backend development
- React + Next.js frontend development
- TypeScript
- Docker containerization
- Linux server administration
- CI/CD with GitHub Actions
- Database management
- Security best practices

**Next Steps:**
- Keep learning and improving
- Add features based on user feedback
- Explore mobile development
- Share your knowledge with others

---

*Phase created: 2026-01-15*
