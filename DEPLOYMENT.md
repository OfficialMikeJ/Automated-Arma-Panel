# Deployment Guide - Tactical Command Panel

Complete guide for deploying Tactical Command in various environments.

## Table of Contents

1. [Docker Deployment](#docker-deployment)
2. [Systemd Deployment](#systemd-deployment)
3. [Production Best Practices](#production-best-practices)
4. [Backup Strategy](#backup-strategy)
5. [Monitoring](#monitoring)
6. [Scaling](#scaling)

---

## Docker Deployment

### Prerequisites

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Quick Start

```bash
cd /app

# Create .env file (optional, for custom config)
cp .env.example .env

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Production Configuration

Edit `docker-compose.yml` for production:

```yaml
services:
  backend:
    environment:
      - SECRET_KEY=${SECRET_KEY}  # Use strong key!
      - CORS_ORIGINS=https://yourdomain.com
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
    restart: unless-stopped
```

### SSL/HTTPS Setup

**Option 1: Nginx Reverse Proxy**

```nginx
# /etc/nginx/sites-available/tactical-command
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Option 2: Traefik (Automatic SSL)**

Add to `docker-compose.yml`:

```yaml
services:
  traefik:
    image: traefik:v2.10
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.myresolver.acme.tlschallenge=true"
      - "--certificatesresolvers.myresolver.acme.email=admin@yourdomain.com"
      - "--certificatesresolvers.myresolver.acme.storage=/letsencrypt/acme.json"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./letsencrypt:/letsencrypt

  frontend:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.frontend.rule=Host(`yourdomain.com`)"
      - "traefik.http.routers.frontend.entrypoints=websecure"
      - "traefik.http.routers.frontend.tls.certresolver=myresolver"
```

---

## Systemd Deployment

### Installation

```bash
cd /app/scripts
sudo ./setup-systemd.sh
```

### Manual Setup (if script fails)

1. **Create systemd services:**
```bash
sudo cp scripts/systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
```

2. **Enable services:**
```bash
sudo systemctl enable tactical-backend
sudo systemctl enable tactical-frontend
```

3. **Start services:**
```bash
sudo systemctl start tactical-backend
sudo systemctl start tactical-frontend
```

### Service Configuration

Edit service files if needed:

```bash
sudo nano /etc/systemd/system/tactical-backend.service
```

After changes:
```bash
sudo systemctl daemon-reload
sudo systemctl restart tactical-backend
```

### Logging

**View live logs:**
```bash
sudo journalctl -u tactical-backend -f
sudo journalctl -u tactical-frontend -f
```

**View recent logs:**
```bash
sudo journalctl -u tactical-backend -n 100
```

**Export logs:**
```bash
sudo journalctl -u tactical-backend --since today > backend.log
```

---

## Production Best Practices

### 1. Security

**Environment Variables:**
```bash
# Generate strong secret key
openssl rand -hex 32

# Set in backend/.env
SECRET_KEY=your-generated-key-here
```

**Firewall Configuration:**
```bash
# Allow only necessary ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# If exposing MongoDB (not recommended)
sudo ufw allow from your.ip.address to any port 27017
```

**MongoDB Security:**
```javascript
// Connect to MongoDB
mongosh

// Create admin user
use admin
db.createUser({
  user: "admin",
  pwd: "strong-password",
  roles: [ { role: "userAdminAnyDatabase", db: "admin" } ]
})

// Create app user
use arma_server_panel
db.createUser({
  user: "tactical_user",
  pwd: "app-password",
  roles: [ { role: "readWrite", db: "arma_server_panel" } ]
})
```

Update backend/.env:
```env
MONGO_URL=mongodb://tactical_user:app-password@localhost:27017
```

### 2. Performance Optimization

**Backend:**
- Use production ASGI server (uvicorn with workers)
- Enable gzip compression
- Set appropriate worker count

```bash
# In systemd service or docker-compose
uvicorn server:app --host 0.0.0.0 --port 8001 --workers 4
```

**Frontend:**
- Enable nginx gzip
- Set proper cache headers
- Use CDN for static assets

**MongoDB:**
- Create indexes on frequently queried fields
```javascript
db.servers.createIndex({ "user_id": 1 })
db.servers.createIndex({ "status": 1 })
db.mods.createIndex({ "server_id": 1 })
```

### 3. Resource Limits

**Docker Compose:**
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
  
  mongodb:
    deploy:
      resources:
        limits:
          memory: 1G
```

**Systemd:**
Edit service files:
```ini
[Service]
MemoryLimit=2G
CPUQuota=200%
```

---

## Backup Strategy

### Automated Backups

**Daily Backups (cron):**
```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /app/scripts/backup.sh daily-$(date +\%Y\%m\%d) >> /app/logs/backup.log 2>&1

# Add weekly backup on Sunday
0 3 * * 0 /app/scripts/backup.sh weekly-$(date +\%Y\%m\%d) >> /app/logs/backup.log 2>&1
```

### Offsite Backups

**Upload to S3:**
```bash
#!/bin/bash
BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S)"
/app/scripts/backup.sh $BACKUP_NAME

# Upload to S3
aws s3 cp /app/backups/${BACKUP_NAME}.tar.gz s3://your-bucket/tactical-backups/

# Clean up local copy older than 7 days
find /app/backups -name "*.tar.gz" -mtime +7 -delete
```

**Sync to remote server:**
```bash
#!/bin/bash
BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S)"
/app/scripts/backup.sh $BACKUP_NAME

# Rsync to remote server
rsync -avz /app/backups/${BACKUP_NAME}.tar.gz user@backup-server:/backups/tactical/
```

### Backup Testing

Regularly test restores:
```bash
# Test restore in staging environment
./restore.sh backup_20240127_153045

# Verify data integrity
# Test login
# Check server instances
# Verify configurations
```

---

## Monitoring

### Health Checks

**Docker:**
```bash
# Check container health
docker ps
docker inspect tactical-backend | grep -A 10 Health
```

**Systemd:**
```bash
# Service status
systemctl status tactical-backend

# Failed services
systemctl --failed
```

### Application Monitoring

**Simple monitoring script:**
```bash
#!/bin/bash
# /app/scripts/health-check.sh

# Check backend
if curl -f http://localhost:8001/api/ > /dev/null 2>&1; then
    echo "✓ Backend OK"
else
    echo "✗ Backend DOWN"
    sudo systemctl restart tactical-backend
fi

# Check frontend
if curl -f http://localhost:3000/ > /dev/null 2>&1; then
    echo "✓ Frontend OK"
else
    echo "✗ Frontend DOWN"
    sudo systemctl restart tactical-frontend
fi

# Check MongoDB
if mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
    echo "✓ MongoDB OK"
else
    echo "✗ MongoDB DOWN"
    sudo systemctl restart mongod
fi
```

**Add to cron:**
```bash
*/5 * * * * /app/scripts/health-check.sh >> /app/logs/health.log 2>&1
```

### Metrics Collection

**Prometheus + Grafana:**
See advanced monitoring guide for full setup.

**Simple metrics:**
```bash
# CPU and Memory usage
htop

# Docker stats
docker stats

# MongoDB metrics
mongosh --eval "db.serverStatus()"
```

---

## Scaling

### Horizontal Scaling

**Backend scaling with Docker:**
```yaml
services:
  backend:
    deploy:
      replicas: 3
    
  nginx-lb:
    image: nginx:alpine
    volumes:
      - ./nginx-lb.conf:/etc/nginx/nginx.conf
```

**Nginx load balancer config:**
```nginx
upstream backend {
    server backend:8001;
    # Add more backend instances
}

server {
    location /api/ {
        proxy_pass http://backend;
    }
}
```

### Database Scaling

**MongoDB Replica Set:**
For high availability, set up MongoDB replica set.

**Read/Write Splitting:**
Use MongoDB connection with read preference:
```python
client = AsyncIOMotorClient(
    mongo_url,
    readPreference='secondaryPreferred'
)
```

### Caching

**Redis for session storage:**
Add Redis to docker-compose.yml:
```yaml
services:
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

---

## Troubleshooting

### Common Issues

**Backend won't start:**
```bash
# Check logs
docker logs tactical-backend
# or
sudo journalctl -u tactical-backend -n 50

# Common fixes:
# - Check MongoDB is running
# - Verify .env configuration
# - Check port availability
```

**Database connection errors:**
```bash
# Test MongoDB connection
mongosh mongodb://localhost:27017

# Check MongoDB status
sudo systemctl status mongod

# Restart MongoDB
sudo systemctl restart mongod
```

**Out of memory:**
```bash
# Check memory usage
free -h
docker stats

# Increase limits or add swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## Support

For issues or questions:
- Check logs first
- Review this guide
- Open GitHub issue
- Contact support

---

**Remember:**
- Always test in staging first
- Keep backups before major changes
- Monitor resource usage
- Update dependencies regularly
- Review security settings quarterly
