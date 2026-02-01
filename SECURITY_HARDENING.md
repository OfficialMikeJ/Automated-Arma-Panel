# Security Hardening Guide - Tactical Server Control Panel

## Overview

This guide provides comprehensive security recommendations for production deployment of the Tactical Server Control Panel.

## Table of Contents
1. [Pre-Production Checklist](#pre-production-checklist)
2. [Network Security](#network-security)
3. [Application Security](#application-security)
4. [Database Security](#database-security)
5. [User Authentication](#user-authentication)
6. [SSL/TLS Configuration](#ssltls-configuration)
7. [Server Hardening](#server-hardening)
8. [Monitoring & Logging](#monitoring--logging)
9. [Backup & Recovery](#backup--recovery)
10. [Security Audit Checklist](#security-audit-checklist)

---

## Pre-Production Checklist

Before deploying to production, verify:

- [ ] All default passwords changed
- [ ] Strong admin password set (12+ characters)
- [ ] TOTP/2FA enabled for admin accounts
- [ ] Security questions configured
- [ ] SSL/TLS certificate installed
- [ ] Firewall configured
- [ ] MongoDB access restricted
- [ ] SSH key-based authentication enabled
- [ ] Unnecessary services disabled
- [ ] Log monitoring configured
- [ ] Backup system tested
- [ ] Update procedure tested

---

## Network Security

### Firewall Configuration

**Essential Rules:**
```bash
# Allow only necessary ports
sudo ufw default deny incoming
sudo ufw default allow outgoing

# SSH (change 22 to custom port for better security)
sudo ufw allow 22/tcp

# Panel access (use SSL/443 in production)
sudo ufw allow 3000/tcp  # Or 443/tcp with nginx
sudo ufw allow 8001/tcp  # Backend API

# Game server ports
sudo ufw allow 2001:2100/tcp
sudo ufw allow 2001:2100/udp

# Enable
sudo ufw enable
```

**Advanced: IP Whitelisting**
```bash
# Allow panel access only from specific IPs
sudo ufw delete allow 3000/tcp
sudo ufw allow from 192.168.1.0/24 to any port 3000 proto tcp

# Allow SSH only from management IP
sudo ufw limit from 203.0.113.10 to any port 22 proto tcp
```

### Change Default Ports

**Security through obscurity (additional layer):**

**Frontend:**
```bash
# Edit systemd service
sudo nano /etc/systemd/system/tactical-frontend.service
Environment="PORT=8443"  # Change from 3000

# Update firewall
sudo ufw delete allow 3000/tcp
sudo ufw allow 8443/tcp

sudo systemctl daemon-reload
sudo systemctl restart tactical-frontend
```

**Backend:**
```bash
# Edit systemd service
sudo nano /etc/systemd/system/tactical-backend.service
ExecStart=...--port 8444  # Change from 8001

# Update firewall
sudo ufw delete allow 8001/tcp
sudo ufw allow 8444/tcp

sudo systemctl daemon-reload
sudo systemctl restart tactical-backend
```

### Network Segmentation

**Isolate Services:**
```bash
# MongoDB should ONLY listen on localhost
sudo nano /etc/mongod.conf

# Set:
net:
  bindIp: 127.0.0.1
  port: 27017

sudo systemctl restart mongod
```

### Rate Limiting

**Protect Against Brute Force:**

Install fail2ban:
```bash
sudo apt-get install fail2ban

# Create filter for panel
sudo nano /etc/fail2ban/filter.d/tactical-panel.conf
```

Add content:
```ini
[Definition]
failregex = ^.*\"POST /api/auth/login HTTP.*\" 401.*$
ignoreregex =
```

Configure jail:
```bash
sudo nano /etc/fail2ban/jail.local
```

Add:
```ini
[tactical-panel]
enabled = true
port = 3000,8001
filter = tactical-panel
logpath = /var/log/nginx/access.log
maxretry = 5
findtime = 600
bantime = 3600
```

Restart:
```bash
sudo systemctl restart fail2ban
```

---

## Application Security

### Environment Variables

**Never hardcode sensitive data!**

**Check .env files:**
```bash
cat /app/backend/.env
cat /app/frontend/.env
```

**Secure .env files:**
```bash
chmod 600 /app/backend/.env
chmod 600 /app/frontend/.env
chown root:root /app/backend/.env
chown root:root /app/frontend/.env
```

**Generate Strong Secrets:**
```bash
# JWT Secret (at least 32 bytes)
openssl rand -hex 32

# MongoDB password (if using auth)
openssl rand -base64 24
```

### CORS Configuration

**Restrict Origins:**
```bash
# Edit backend .env
nano /app/backend/.env

# Production: Specific origins only
CORS_ORIGINS="https://yourdomain.com,https://panel.yourdomain.com"

# Development only:
# CORS_ORIGINS="*"
```

### API Security

**Rate Limiting (Application Level):**

Add to `/app/backend/server.py`:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@api_router.post("/auth/login")
@limiter.limit("5/minute")  # 5 attempts per minute
async def login(request: Request, ...):
    ...
```

Install dependency:
```bash
cd /app/backend
source venv/bin/activate
pip install slowapi
pip freeze > requirements.txt
```

### Input Validation

**Already Implemented:**
- ✅ Password complexity requirements
- ✅ Username validation
- ✅ Email format validation
- ✅ Port number ranges
- ✅ IP address validation

**Verify it's enabled:**
```bash
grep -A 10 "PASSWORD_MIN_LENGTH" /app/backend/.env

# Should have:
PASSWORD_MIN_LENGTH=8
PASSWORD_REQUIRE_UPPERCASE=true
PASSWORD_REQUIRE_LOWERCASE=true
PASSWORD_REQUIRE_NUMBERS=true
PASSWORD_REQUIRE_SPECIAL=true
```

### Content Security Policy

**Add CSP Headers (via nginx):**
```nginx
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https://yourdomain.com:8001;" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "DENY" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

---

## Database Security

### MongoDB Authentication

**Enable Authentication:**
```bash
# Create admin user
mongosh

use admin
db.createUser({
  user: "admin",
  pwd: passwordPrompt(),  // Enter strong password
  roles: ["userAdminAnyDatabase", "readWriteAnyDatabase"]
})

use tactical_panel
db.createUser({
  user: "tactical_user",
  pwd: passwordPrompt(),
  roles: ["readWrite"]
})

exit
```

**Enable Auth in Config:**
```bash
sudo nano /etc/mongod.conf

# Add:
security:
  authorization: enabled

sudo systemctl restart mongod
```

**Update Backend .env:**
```bash
nano /app/backend/.env

# Change:
MONGO_URL="mongodb://tactical_user:YOUR_PASSWORD@localhost:27017/tactical_panel"
```

### Database Encryption

**Enable Encryption at Rest:**
```bash
sudo nano /etc/mongod.conf

# Add:
security:
  enableEncryption: true
  encryptionKeyFile: /etc/mongodb-keyfile

# Generate key
openssl rand -base64 32 > /etc/mongodb-keyfile
chmod 600 /etc/mongodb-keyfile
chown mongodb:mongodb /etc/mongodb-keyfile

sudo systemctl restart mongod
```

### Regular Backups

**Automated Backup Script:**
```bash
# The panel includes backup.sh
cat /app/scripts/backup.sh

# Setup cron job
sudo crontab -e

# Add (daily at 2 AM):
0 2 * * * /app/scripts/backup.sh > /var/log/tactical-backup.log 2>&1
```

**Verify Backups:**
```bash
ls -lh /app/backups/
```

---

## User Authentication

### Password Policy

**Already Enforced:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

**Increase Minimum Length (Recommended):**
```bash
nano /app/backend/.env

# Change:
PASSWORD_MIN_LENGTH=12  # or 16 for maximum security
```

### Two-Factor Authentication (TOTP)

**Enforce TOTP for All Users:**

Add to `/app/backend/server.py`:
```python
# After user login, check TOTP
if user.get("totp_enabled"):
    if not totp_code:
        return {"message": "TOTP code required", "requires_totp": True}
    # Verify TOTP
    ...
```

**Require TOTP Setup:**
```bash
# Add to .env
REQUIRE_TOTP=true
```

### Session Management

**Configure Session Timeout:**
```bash
nano /app/backend/.env

# Set session timeout (minutes)
SESSION_TIMEOUT_MINUTES=30  # 30 minutes idle timeout
```

**Invalidate on Password Change:**

Add to `/app/backend/server.py`:
```python
# When password is changed
await db.sessions.delete_many({"user_id": user_id})
```

### Account Lockout

**Implement Lockout Policy:**

Add to `/app/backend/server.py`:
```python
# Track failed attempts
failed_attempts = await db.login_attempts.count_documents({
    "username": username,
    "success": False,
    "timestamp": {"$gt": datetime.now(timezone.utc) - timedelta(minutes=15)}
})

if failed_attempts >= 5:
    raise HTTPException(
        status_code=429,
        detail="Account locked due to too many failed attempts. Try again in 15 minutes."
    )
```

---

## SSL/TLS Configuration

### Install Let's Encrypt Certificate

**Use the Installer:**
```bash
cd /app/scripts
sudo bash ./install.sh
# Select Option 3: Install SSL Certificates
```

**Or Manual Installation:**
```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com -d panel.yourdomain.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### Nginx SSL Configuration

**Strong SSL Settings:**
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_stapling on;
    ssl_stapling_verify on;

    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

---

## Server Hardening

### SSH Security

**Disable Password Authentication:**
```bash
# Generate SSH key (on your local machine)
ssh-keygen -t ed25519 -C "your_email@example.com"

# Copy to server
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@server

# Disable password auth
sudo nano /etc/ssh/sshd_config

# Set:
PasswordAuthentication no
PermitRootLogin no
PubkeyAuthentication yes

sudo systemctl restart sshd
```

**Change SSH Port:**
```bash
sudo nano /etc/ssh/sshd_config

# Change:
Port 2222  # Use custom port

sudo systemctl restart sshd

# Update firewall
sudo ufw allow 2222/tcp
sudo ufw delete allow 22/tcp
```

### Disable Unnecessary Services

```bash
# List all services
systemctl list-unit-files --type=service

# Disable unused ones
sudo systemctl disable bluetooth.service
sudo systemctl disable cups.service
sudo systemctl stop bluetooth.service
sudo systemctl stop cups.service
```

### Keep System Updated

```bash
# Setup unattended upgrades
sudo apt-get install unattended-upgrades

# Enable
sudo dpkg-reconfigure --priority=low unattended-upgrades

# Or manual updates
sudo apt-get update
sudo apt-get upgrade -y
```

### File System Permissions

```bash
# Secure application files
chown -R root:root /app
chmod -R 755 /app

# Secure config files
chmod 600 /app/backend/.env
chmod 600 /app/frontend/.env

# Secure scripts
chmod 750 /app/scripts/*.sh

# Secure logs
mkdir -p /var/log/tactical
chmod 750 /var/log/tactical
```

---

## Monitoring & Logging

### Log Aggregation

**Centralized Logging:**
```bash
# Install rsyslog
sudo apt-get install rsyslog

# Configure remote logging
sudo nano /etc/rsyslog.conf

# Add:
*.* @@log-server:514
```

### Log Rotation

**Configure logrotate:**
```bash
sudo nano /etc/logrotate.d/tactical-panel
```

Add:
```
/var/log/tactical/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 640 root root
    sharedscripts
    postrotate
        systemctl reload tactical-backend tactical-frontend
    endscript
}
```

### Monitoring Setup

**Install Monitoring Tools:**
```bash
# Netdata (real-time monitoring)
bash <(curl -Ss https://my-netdata.io/kickstart.sh)

# Access at: http://your-server:19999
```

**Alert Configuration:**
```bash
# Email alerts
sudo nano /etc/netdata/health_alarm_notify.conf

# Set:
SEND_EMAIL="YES"
DEFAULT_RECIPIENT_EMAIL="admin@yourdomain.com"
```

### Security Monitoring

**Monitor Failed Login Attempts:**
```bash
# View failed attempts
sudo journalctl -u tactical-backend | grep "401"

# Create alert script
cat > /usr/local/bin/check-failed-logins.sh << 'EOF'
#!/bin/bash
FAILED=$(journalctl -u tactical-backend --since "5 minutes ago" | grep -c "401")
if [ $FAILED -gt 10 ]; then
    echo "WARNING: $FAILED failed login attempts in last 5 minutes" | mail -s "Security Alert" admin@yourdomain.com
fi
EOF

chmod +x /usr/local/bin/check-failed-logins.sh

# Run every 5 minutes
crontab -e
# Add:
*/5 * * * * /usr/local/bin/check-failed-logins.sh
```

---

## Backup & Recovery

### Backup Strategy

**What to Backup:**
1. Database (MongoDB)
2. Configuration files (.env)
3. Server configs (systemd, nginx)
4. User data
5. Logs (optional)

**Automated Backup:**
```bash
# Use included backup script
/app/scripts/backup.sh

# Schedule via cron
0 2 * * * /app/scripts/backup.sh > /var/log/backup.log 2>&1

# Backup to remote location
0 3 * * * rsync -avz /app/backups/ backup-server:/backups/tactical/
```

### Disaster Recovery

**Test Recovery Process:**
```bash
# Restore from backup
/app/scripts/restore.sh /app/backups/backup_20250201_020000.tar.gz

# Verify services
sudo systemctl status tactical-backend tactical-frontend

# Test access
curl http://localhost:3000
curl http://localhost:8001/api/auth/check-first-run
```

---

## Security Audit Checklist

### Pre-Deployment

- [ ] Change all default passwords
- [ ] Enable TOTP for admin accounts
- [ ] Configure strong password policy
- [ ] Set session timeouts
- [ ] Enable MongoDB authentication
- [ ] Restrict MongoDB to localhost
- [ ] Install SSL certificate
- [ ] Configure firewall rules
- [ ] Disable unnecessary services
- [ ] Setup SSH key authentication
- [ ] Disable root SSH login
- [ ] Change default ports (optional)
- [ ] Configure log rotation
- [ ] Setup automated backups
- [ ] Test backup restoration
- [ ] Configure monitoring alerts
- [ ] Setup fail2ban
- [ ] Enable unattended upgrades

### Post-Deployment

- [ ] Verify all services running
- [ ] Test SSL certificate
- [ ] Verify firewall rules active
- [ ] Check log files for errors
- [ ] Test backup system
- [ ] Verify monitoring working
- [ ] Test failover procedures
- [ ] Review access logs
- [ ] Audit user accounts
- [ ] Test TOTP enforcement
- [ ] Verify rate limiting
- [ ] Check for security updates

### Monthly Maintenance

- [ ] Review access logs
- [ ] Check for failed login attempts
- [ ] Verify backups successful
- [ ] Test backup restoration
- [ ] Update system packages
- [ ] Review user accounts
- [ ] Check SSL certificate expiry
- [ ] Review firewall logs
- [ ] Monitor disk space
- [ ] Check service health
- [ ] Review security advisories

### Security Incident Response

**If Breach Suspected:**

1. **Isolate:**
   ```bash
   sudo ufw deny 3000/tcp
   sudo ufw deny 8001/tcp
   ```

2. **Investigate:**
   ```bash
   sudo journalctl -u tactical-backend -u tactical-frontend --since "24 hours ago" > /tmp/investigation.log
   ```

3. **Reset Credentials:**
   ```bash
   # Change JWT secret
   echo "SECRET_KEY=$(openssl rand -hex 32)" | sudo tee -a /app/backend/.env
   
   # Force all users to re-login
   mongosh
   use tactical_panel
   db.sessions.deleteMany({})
   ```

4. **Notify Users**

5. **Review and Patch**

---

## Additional Resources

### Security Tools

- **OWASP ZAP:** Web application security scanner
- **Nmap:** Network discovery and security auditing
- **Lynis:** Security auditing tool
- **ClamAV:** Antivirus engine
- **AIDE:** File integrity checker

### Security Guides

- OWASP Top 10: https://owasp.org/www-project-top-ten/
- CIS Benchmarks: https://www.cisecurity.org/cis-benchmarks/
- MongoDB Security Checklist: https://docs.mongodb.com/manual/administration/security-checklist/

---

## Summary

Following this guide will significantly improve your panel's security posture. Remember:

1. **Defense in Depth:** Multiple layers of security
2. **Principle of Least Privilege:** Grant minimum necessary permissions
3. **Keep Updated:** Regular security updates are critical
4. **Monitor Continuously:** Active monitoring and alerting
5. **Test Regularly:** Verify security measures work
6. **Document Everything:** Maintain security documentation
7. **Backup Always:** Regular tested backups

Security is an ongoing process, not a one-time setup!
