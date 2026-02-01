# Production Deployment Guide

## Complete Guide to Deploying Tactical Server Control Panel in Production

This guide provides step-by-step instructions for deploying the panel in a production environment with high availability, security, and performance.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Server Requirements](#server-requirements)
3. [Installation Methods](#installation-methods)
4. [Production Configuration](#production-configuration)
5. [SSL/TLS Setup](#ssltls-setup)
6. [Reverse Proxy Configuration](#reverse-proxy-configuration)
7. [Database Optimization](#database-optimization)
8. [Performance Tuning](#performance-tuning)
9. [High Availability Setup](#high-availability-setup)
10. [Monitoring & Alerting](#monitoring--alerting)
11. [Backup Strategy](#backup-strategy)
12. [Maintenance Procedures](#maintenance-procedures)

---

## Prerequisites

### Domain & DNS
- Domain name registered
- DNS A record pointing to your server IP
- (Optional) Wildcard DNS for subdomains

### Server Access
- Root or sudo access
- SSH key-based authentication configured
- Static IP address assigned

### Required Knowledge
- Linux command line
- Basic networking concepts
- Web server configuration (nginx)
- Database management (MongoDB)

---

## Server Requirements

### Minimum Specifications

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **CPU** | 2 cores | 4+ cores |
| **RAM** | 2 GB | 4+ GB |
| **Storage** | 20 GB SSD | 50+ GB SSD |
| **Network** | 100 Mbps | 1 Gbps |
| **OS** | Ubuntu 20.04+ | Ubuntu 22.04 LTS |

### Additional Requirements
- Swap space: 2x RAM size
- Open ports: 80, 443, 2001-2100
- Backup storage (off-server)

### Supported Operating Systems
- ✅ Ubuntu 20.04/22.04 LTS (Recommended)
- ✅ Debian 10/11
- ✅ CentOS 7/8
- ✅ RHEL 7/8

---

## Installation Methods

### Method 1: Automated Installer (Recommended)

**Step 1: Download Application**
```bash
# Clone or download to /app
cd /tmp
# Download your packaged application
tar -xzf tactical-panel.tar.gz
sudo mv tactical-panel /app
cd /app
```

**Step 2: Run Installer**
```bash
cd /app/scripts
sudo bash ./install.sh
```

**Step 3: Select Options**
```
1. Install Panel (Native) + Guided Setup
2. Configure Firewall (UFW)
3. Install SSL Certificates (Let's Encrypt)
```

The installer will:
- ✅ Auto-install Python 3 & Node.js
- ✅ Install MongoDB
- ✅ Create virtual environments
- ✅ Install dependencies
- ✅ Configure systemd services
- ✅ Setup firewall rules
- ✅ Install SSL certificates

### Method 2: Manual Installation

**Step 1: Install Dependencies**
```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Python
sudo apt-get install -y python3 python3-pip python3-venv

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install MongoDB
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu $(lsb_release -cs)/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org
sudo systemctl start mongod
sudo systemctl enable mongod

# Install nginx
sudo apt-get install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

**Step 2: Setup Application**
```bash
# Backend
cd /app/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate

# Frontend
cd /app/frontend
npm install -g yarn
yarn install
```

**Step 3: Configure Environment**
```bash
# Backend .env
cat > /app/backend/.env << EOF
MONGO_URL="mongodb://localhost:27017"
DB_NAME="tactical_panel"
SECRET_KEY="$(openssl rand -hex 32)"
CORS_ORIGINS="https://yourdomain.com"
PASSWORD_MIN_LENGTH=12
PASSWORD_REQUIRE_UPPERCASE=true
PASSWORD_REQUIRE_LOWERCASE=true
PASSWORD_REQUIRE_NUMBERS=true
PASSWORD_REQUIRE_SPECIAL=true
SESSION_TIMEOUT_MINUTES=30
EOF

# Frontend .env
cat > /app/frontend/.env << EOF
REACT_APP_BACKEND_URL=https://yourdomain.com
EOF
```

**Step 4: Setup Systemd Services**
```bash
# Copy service files
sudo cp /app/scripts/systemd/tactical-backend.service /etc/systemd/system/
sudo cp /app/scripts/systemd/tactical-frontend.service /etc/systemd/system/

# Reload and enable
sudo systemctl daemon-reload
sudo systemctl enable tactical-backend tactical-frontend
sudo systemctl start tactical-backend tactical-frontend
```

---

## Production Configuration

### Environment Variables

**Backend (`/app/backend/.env`):**
```env
# Database
MONGO_URL="mongodb://tactical_user:STRONG_PASSWORD@localhost:27017/tactical_panel"
DB_NAME="tactical_panel"

# Security
SECRET_KEY="generate-with-openssl-rand-hex-32"
JWT_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=60

# CORS - Use specific domains in production
CORS_ORIGINS="https://panel.yourdomain.com,https://yourdomain.com"

# Password Policy
PASSWORD_MIN_LENGTH=12
PASSWORD_REQUIRE_UPPERCASE=true
PASSWORD_REQUIRE_LOWERCASE=true
PASSWORD_REQUIRE_NUMBERS=true
PASSWORD_REQUIRE_SPECIAL=true

# Session Management
SESSION_TIMEOUT_MINUTES=30

# Logging
LOG_LEVEL="INFO"  # Use INFO or WARNING in production, not DEBUG
```

**Frontend (`/app/frontend/.env`):**
```env
# API endpoint - Use HTTPS in production
REACT_APP_BACKEND_URL=https://panel.yourdomain.com

# Environment
NODE_ENV=production
```

### File Permissions

```bash
# Secure application files
sudo chown -R www-data:www-data /app
sudo chmod -R 755 /app

# Secure configuration files
sudo chmod 600 /app/backend/.env
sudo chmod 600 /app/frontend/.env

# Secure scripts
sudo chmod 750 /app/scripts/*.sh
```

---

## SSL/TLS Setup

### Option 1: Let's Encrypt (Recommended - Free)

**Install Certbot:**
```bash
sudo apt-get install certbot python3-certbot-nginx
```

**Obtain Certificate:**
```bash
sudo certbot --nginx -d yourdomain.com -d panel.yourdomain.com

# Follow prompts:
# - Enter email address
# - Agree to terms
# - Choose redirect HTTP to HTTPS
```

**Auto-Renewal:**
```bash
# Test renewal
sudo certbot renew --dry-run

# Enable automatic renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### Option 2: Commercial Certificate

**Install Certificate:**
```bash
# Copy certificate files
sudo cp yourdomain.com.crt /etc/ssl/certs/
sudo cp yourdomain.com.key /etc/ssl/private/
sudo cp ca-bundle.crt /etc/ssl/certs/

# Set permissions
sudo chmod 644 /etc/ssl/certs/yourdomain.com.crt
sudo chmod 600 /etc/ssl/private/yourdomain.com.key
```

**Configure nginx (see next section)**

### Certificate Monitoring

**Setup Expiry Alert:**
```bash
# Install ssl-cert-check
wget http://www.linux-admins.net/wp-content/uploads/2012/06/ssl-cert-check
sudo chmod +x ssl-cert-check
sudo mv ssl-cert-check /usr/local/bin/

# Create alert script
cat > /usr/local/bin/check-ssl-expiry.sh << 'EOF'
#!/bin/bash
/usr/local/bin/ssl-cert-check -s yourdomain.com -p 443 -n -x 30 | mail -s "SSL Certificate Expiring Soon" admin@yourdomain.com
EOF

chmod +x /usr/local/bin/check-ssl-expiry.sh

# Run weekly
echo "0 9 * * 1 /usr/local/bin/check-ssl-expiry.sh" | sudo crontab -
```

---

## Reverse Proxy Configuration

### Nginx Configuration

**Create Configuration File:**
```bash
sudo nano /etc/nginx/sites-available/tactical-panel
```

**Production Configuration:**
```nginx
# Rate limiting
limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
limit_req_zone $binary_remote_addr zone=api:10m rate=100r/m;

# Upstream servers
upstream backend {
    server localhost:8001 max_fails=3 fail_timeout=30s;
    keepalive 32;
}

upstream frontend {
    server localhost:3000 max_fails=3 fail_timeout=30s;
    keepalive 32;
}

# HTTP - Redirect to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name panel.yourdomain.com yourdomain.com;
    
    # ACME challenge for Let's Encrypt
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    # Redirect all other traffic to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS - Main Configuration
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name panel.yourdomain.com yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/panel.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/panel.yourdomain.com/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/panel.yourdomain.com/chain.pem;

    # SSL Parameters
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;
    ssl_session_timeout 1d;
    ssl_session_cache shared:MozSSL:10m;
    ssl_session_tickets off;

    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    resolver 8.8.8.8 8.8.4.4 valid=300s;
    resolver_timeout 5s;

    # Security Headers
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https://panel.yourdomain.com;" always;

    # Logging
    access_log /var/log/nginx/tactical-access.log combined;
    error_log /var/log/nginx/tactical-error.log warn;

    # Max upload size
    client_max_body_size 100M;

    # API Endpoints
    location /api {
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Login endpoint - stricter rate limiting
    location /api/auth/login {
        limit_req zone=login burst=2 nodelay;
        
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Frontend - React App
    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # WebSocket support
        proxy_read_timeout 86400;
    }

    # Static files caching
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
        proxy_pass http://frontend;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "OK\n";
        add_header Content-Type text/plain;
    }
}
```

**Enable Configuration:**
```bash
# Test configuration
sudo nginx -t

# Create symlink
sudo ln -s /etc/nginx/sites-available/tactical-panel /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Reload nginx
sudo systemctl reload nginx
```

### Apache Configuration (Alternative)

If using Apache instead of nginx:

```bash
sudo a2enmod proxy proxy_http proxy_wstunnel ssl headers rewrite

sudo nano /etc/apache2/sites-available/tactical-panel.conf
```

```apache
<VirtualHost *:443>
    ServerName panel.yourdomain.com
    
    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/panel.yourdomain.com/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/panel.yourdomain.com/privkey.pem
    
    # Security headers
    Header always set Strict-Transport-Security "max-age=63072000"
    Header always set X-Frame-Options "DENY"
    Header always set X-Content-Type-Options "nosniff"
    
    # Backend API
    ProxyPass /api http://localhost:8001/api
    ProxyPassReverse /api http://localhost:8001/api
    
    # Frontend
    ProxyPass / http://localhost:3000/
    ProxyPassReverse / http://localhost:3000/
    
    # WebSocket
    ProxyPass /ws ws://localhost:3000/ws
    ProxyPassReverse /ws ws://localhost:3000/ws
</VirtualHost>

<VirtualHost *:80>
    ServerName panel.yourdomain.com
    Redirect permanent / https://panel.yourdomain.com/
</VirtualHost>
```

```bash
sudo a2ensite tactical-panel
sudo systemctl reload apache2
```

---

## Database Optimization

### MongoDB Production Configuration

**Edit MongoDB Config:**
```bash
sudo nano /etc/mongod.conf
```

**Production Settings:**
```yaml
# Network interfaces
net:
  port: 27017
  bindIp: 127.0.0.1  # Localhost only for security

# Storage
storage:
  dbPath: /var/lib/mongodb
  journal:
    enabled: true
  engine: wiredTiger
  wiredTiger:
    engineConfig:
      cacheSizeGB: 2  # Set to ~50% of available RAM

# Security
security:
  authorization: enabled

# Logging
systemLog:
  destination: file
  logAppend: true
  path: /var/log/mongodb/mongod.log
  logRotate: reopen

# Process Management
processManagement:
  fork: true
  pidFilePath: /var/run/mongodb/mongod.pid

# Operation Profiling
operationProfiling:
  mode: slowOp
  slowOpThresholdMs: 100
```

**Restart MongoDB:**
```bash
sudo systemctl restart mongod
```

### Database Indexing

**Create Indexes for Performance:**
```bash
mongosh
use tactical_panel

# User indexes
db.users.createIndex({ "username": 1 }, { unique: true })
db.users.createIndex({ "id": 1 }, { unique: true })

# Server indexes
db.servers.createIndex({ "id": 1 }, { unique: true })
db.servers.createIndex({ "user_id": 1 })
db.servers.createIndex({ "status": 1 })

# Session indexes
db.sessions.createIndex({ "user_id": 1 })
db.sessions.createIndex({ "created_at": 1 }, { expireAfterSeconds: 3600 })

exit
```

---

## Performance Tuning

### Backend (Uvicorn) Optimization

**Edit systemd service:**
```bash
sudo nano /etc/systemd/system/tactical-backend.service
```

**Optimize workers:**
```ini
ExecStart=/root/.venv/bin/uvicorn server:app \
  --host 0.0.0.0 \
  --port 8001 \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --limit-concurrency 1000 \
  --limit-max-requests 10000 \
  --timeout-keep-alive 5
```

**Worker count formula:** `(2 x CPU_cores) + 1`

### Frontend (React) Optimization

**Build for Production:**
```bash
cd /app/frontend
NODE_ENV=production yarn build

# Serve built files with nginx instead of yarn start
```

**Update nginx to serve static build:**
```nginx
location / {
    root /app/frontend/build;
    try_files $uri /index.html;
    
    # Caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### System Level Tuning

**Increase File Descriptors:**
```bash
sudo nano /etc/security/limits.conf
```

Add:
```
* soft nofile 65536
* hard nofile 65536
root soft nofile 65536
root hard nofile 65536
```

**Optimize Network Stack:**
```bash
sudo nano /etc/sysctl.conf
```

Add:
```
# TCP optimization
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 8192
net.ipv4.tcp_fin_timeout = 15
net.ipv4.tcp_keepalive_time = 300
net.ipv4.tcp_keepalive_probes = 5
net.ipv4.tcp_keepalive_intvl = 15
```

Apply:
```bash
sudo sysctl -p
```

---

## High Availability Setup

### Load Balancer Configuration

**Using nginx as Load Balancer:**

```nginx
upstream backend_cluster {
    least_conn;
    server 192.168.1.10:8001 max_fails=3 fail_timeout=30s;
    server 192.168.1.11:8001 max_fails=3 fail_timeout=30s;
    server 192.168.1.12:8001 max_fails=3 fail_timeout=30s backup;
}

upstream frontend_cluster {
    ip_hash;  # Sticky sessions
    server 192.168.1.10:3000 max_fails=3 fail_timeout=30s;
    server 192.168.1.11:3000 max_fails=3 fail_timeout=30s;
}

server {
    listen 443 ssl http2;
    server_name panel.yourdomain.com;
    
    # ... SSL config ...
    
    location /api {
        proxy_pass http://backend_cluster;
        # ... proxy settings ...
    }
    
    location / {
        proxy_pass http://frontend_cluster;
        # ... proxy settings ...
    }
}
```

### MongoDB Replication

**Setup Replica Set:**

On each MongoDB server:
```bash
sudo nano /etc/mongod.conf
```

Add:
```yaml
replication:
  replSetName: "tactical-rs"
```

Initialize replica set:
```bash
mongosh
rs.initiate({
  _id: "tactical-rs",
  members: [
    { _id: 0, host: "mongo1.yourdomain.com:27017" },
    { _id: 1, host: "mongo2.yourdomain.com:27017" },
    { _id: 2, host: "mongo3.yourdomain.com:27017" }
  ]
})
```

Update backend .env:
```env
MONGO_URL="mongodb://mongo1.yourdomain.com:27017,mongo2.yourdomain.com:27017,mongo3.yourdomain.com:27017/tactical_panel?replicaSet=tactical-rs"
```

---

## Monitoring & Alerting

### Install Monitoring Stack

**Prometheus + Grafana:**
```bash
# Install Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.40.0/prometheus-2.40.0.linux-amd64.tar.gz
tar xvfz prometheus-*.tar.gz
sudo mv prometheus-2.40.0.linux-amd64 /opt/prometheus

# Install Grafana
sudo apt-get install -y software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo apt-get update
sudo apt-get install grafana

sudo systemctl enable grafana-server
sudo systemctl start grafana-server
```

### Setup Alerts

**Email Alerts:**
```bash
sudo apt-get install mailutils

# Configure Prometheus alerting
sudo nano /opt/prometheus/alertmanager.yml
```

```yaml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@yourdomain.com'
  smtp_auth_username: 'your-email@gmail.com'
  smtp_auth_password: 'your-app-password'

route:
  receiver: 'email-alerts'
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h

receivers:
  - name: 'email-alerts'
    email_configs:
      - to: 'admin@yourdomain.com'
        headers:
          Subject: 'Production Alert: {{ .GroupLabels.alertname }}'
```

### Uptime Monitoring

**External Monitoring (Recommended):**
- Uptime Robot: https://uptimerobot.com
- Pingdom: https://www.pingdom.com
- StatusCake: https://www.statuscake.com

**Setup Health Check Endpoint:**

Already available in nginx config:
```
https://panel.yourdomain.com/health
```

---

## Backup Strategy

### Automated Backup Script

**Enhanced Backup with Retention:**
```bash
cat > /usr/local/bin/tactical-backup.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/backups/tactical"
RETENTION_DAYS=30
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup MongoDB
mongodump --uri="mongodb://localhost:27017/tactical_panel" --out="$BACKUP_DIR/db_$DATE"
tar -czf "$BACKUP_DIR/db_$DATE.tar.gz" -C "$BACKUP_DIR" "db_$DATE"
rm -rf "$BACKUP_DIR/db_$DATE"

# Backup application files
tar -czf "$BACKUP_DIR/app_$DATE.tar.gz" \
  --exclude='node_modules' \
  --exclude='venv' \
  --exclude='__pycache__' \
  /app

# Backup nginx config
tar -czf "$BACKUP_DIR/nginx_$DATE.tar.gz" /etc/nginx

# Remove old backups
find $BACKUP_DIR -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete

# Upload to remote storage (optional)
# aws s3 sync $BACKUP_DIR s3://your-bucket/tactical-backups/

echo "Backup completed: $DATE"
EOF

chmod +x /usr/local/bin/tactical-backup.sh
```

**Schedule Daily Backups:**
```bash
sudo crontab -e

# Add:
0 2 * * * /usr/local/bin/tactical-backup.sh >> /var/log/tactical-backup.log 2>&1
```

### Offsite Backup

**Sync to Remote Server:**
```bash
# Setup SSH key
ssh-keygen -t ed25519
ssh-copy-id backup@backup-server.com

# Add to backup script:
rsync -avz --delete /backups/tactical/ backup@backup-server.com:/backups/tactical/
```

---

## Maintenance Procedures

### Regular Maintenance Checklist

**Daily:**
- [ ] Check service status
- [ ] Review error logs
- [ ] Monitor disk space
- [ ] Verify backups completed

**Weekly:**
- [ ] Review access logs
- [ ] Check for security updates
- [ ] Monitor performance metrics
- [ ] Test backup restoration

**Monthly:**
- [ ] Update system packages
- [ ] Review user accounts
- [ ] Audit security settings
- [ ] Performance optimization
- [ ] SSL certificate check

### Update Procedure

**Using Update Script:**
```bash
cd /app/scripts
sudo bash ./update-panel.sh
```

**Manual Update:**
```bash
# Backup first
/usr/local/bin/tactical-backup.sh

# Stop services
sudo systemctl stop tactical-backend tactical-frontend

# Update code
cd /app
git pull  # or copy new files

# Update dependencies
cd /app/backend
source venv/bin/activate
pip install -r requirements.txt
deactivate

cd /app/frontend
yarn install

# Restart services
sudo systemctl start tactical-backend tactical-frontend

# Verify
curl https://panel.yourdomain.com/health
```

### Rollback Procedure

**If Update Fails:**
```bash
# Stop services
sudo systemctl stop tactical-backend tactical-frontend

# Restore from backup
cd /app/scripts
./restore.sh /backups/tactical/backup_YYYYMMDD_HHMMSS.tar.gz

# Restart services
sudo systemctl start tactical-backend tactical-frontend

# Verify
sudo systemctl status tactical-backend tactical-frontend
```

---

## Post-Deployment Checklist

- [ ] SSL certificate installed and working
- [ ] All services running
- [ ] Firewall configured
- [ ] MongoDB authentication enabled
- [ ] Backups configured and tested
- [ ] Monitoring configured
- [ ] Log rotation configured
- [ ] DNS records correct
- [ ] Email alerts working
- [ ] First-time setup completed
- [ ] Admin account created with TOTP
- [ ] Documentation updated
- [ ] Team trained on procedures

---

## Support & Resources

### Official Documentation
- README.md - General overview
- INSTALLATION_GUIDE.md - Installation methods
- TROUBLESHOOTING_COMPLETE.md - Issue resolution
- SECURITY_HARDENING.md - Security best practices

### External Resources
- nginx Documentation: https://nginx.org/en/docs/
- MongoDB Production Notes: https://docs.mongodb.com/manual/administration/production-notes/
- Let's Encrypt: https://letsencrypt.org/docs/
- Systemd Documentation: https://www.freedesktop.org/software/systemd/man/

---

## Conclusion

Following this guide ensures a production-ready deployment with:
- ✅ High security
- ✅ Optimal performance
- ✅ High availability
- ✅ Comprehensive monitoring
- ✅ Disaster recovery capability

Remember: Production deployment is an ongoing process requiring regular maintenance, monitoring, and updates!
