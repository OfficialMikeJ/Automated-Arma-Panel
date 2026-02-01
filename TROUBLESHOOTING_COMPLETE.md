# Troubleshooting Guide - Tactical Server Control Panel

## Table of Contents
1. [Installation Issues](#installation-issues)
2. [Service Startup Problems](#service-startup-problems)
3. [Network & Access Issues](#network--access-issues)
4. [Database Connection Issues](#database-connection-issues)
5. [Permission Errors](#permission-errors)
6. [Frontend Issues](#frontend-issues)
7. [Backend API Issues](#backend-api-issues)
8. [Firewall Configuration](#firewall-configuration)
9. [Performance Issues](#performance-issues)
10. [Common Error Messages](#common-error-messages)

---

## Installation Issues

### Issue: "Permission denied" on scripts

**Symptoms:**
```bash
./install.sh: Permission denied
./update-panel.sh: Permission denied
```

**Solution:**
```bash
# Fix all script permissions
cd /app/scripts
sudo bash ./fix-permissions.sh

# Or fix manually
chmod +x /app/scripts/*.sh
sudo bash ./install.sh
```

**Prevention:**
Always use `sudo bash ./script.sh` instead of just `./script.sh`

---

### Issue: "Node.js is required but not installed"

**Symptoms:**
```
[ERROR] ✗ Node.js is required but not installed
Missing dependencies. Please install Node.js 16+ first.
```

**Solution:**
The installer now auto-installs Node.js! Just answer 'Y' when prompted:
```
Would you like to install missing dependencies automatically? (Y/n): Y
```

**Manual Installation:**
```bash
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# RHEL/CentOS
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install -y nodejs
```

---

### Issue: "Python 3 is required but not installed"

**Solution:**
The installer auto-installs Python 3! Answer 'Y' when prompted.

**Manual Installation:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv

# RHEL/CentOS
sudo yum install -y python3 python3-pip
```

---

## Service Startup Problems

### Issue: "Job for tactical-backend.service failed"

**Symptoms:**
```bash
Job for tactical-backend.service failed because of unavailable resources or another system error.
See "systemctl status tactical-backend.service" for details.
```

**Diagnosis:**
```bash
# Check service status
sudo systemctl status tactical-backend

# View full logs
sudo journalctl -xeu tactical-backend --no-pager | tail -100

# Check if port is already in use
sudo lsof -i :8001
```

**Common Causes & Solutions:**

**1. Wrong Virtual Environment Path**
```bash
# Find correct venv
find /app -name "uvicorn" -type f 2>/dev/null
find /root -name "uvicorn" -type f 2>/dev/null

# Edit service file
sudo nano /etc/systemd/system/tactical-backend.service

# Update ExecStart line with correct path:
ExecStart=/correct/path/to/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart tactical-backend
```

**2. Wrong User Permissions**
```bash
# Check what user owns the files
ls -la /app/backend

# Update service to use correct user
sudo nano /etc/systemd/system/tactical-backend.service

# Change:
User=your_username
Group=your_username

sudo systemctl daemon-reload
sudo systemctl restart tactical-backend
```

**3. MongoDB Not Running**
```bash
# Check MongoDB status
sudo systemctl status mongodb  # or mongod

# Start MongoDB
sudo systemctl start mongodb
sudo systemctl enable mongodb

# Verify connection
mongosh --eval "db.version()"
```

**4. Missing Dependencies**
```bash
# Activate venv and reinstall
cd /app/backend
source venv/bin/activate  # or /root/.venv/bin/activate
pip install -r requirements.txt
deactivate

# Restart service
sudo systemctl restart tactical-backend
```

**5. Port Already in Use**
```bash
# Find what's using port 8001
sudo lsof -i :8001
sudo netstat -tlnp | grep 8001

# Kill the process
sudo kill -9 <PID>

# Or stop conflicting service
sudo systemctl stop supervisor  # if using both supervisor and systemd
```

---

### Issue: Frontend Service Won't Start

**Diagnosis:**
```bash
sudo systemctl status tactical-frontend
sudo journalctl -xeu tactical-frontend --no-pager | tail -100
```

**Common Solutions:**

**1. Node Modules Not Installed**
```bash
cd /app/frontend
yarn install
sudo systemctl restart tactical-frontend
```

**2. Port 3000 Already in Use**
```bash
sudo lsof -i :3000
sudo kill -9 <PID>
sudo systemctl restart tactical-frontend
```

**3. Wrong Environment Variables**
```bash
# Check .env file
cat /app/frontend/.env

# Should contain:
REACT_APP_BACKEND_URL=http://your-server-ip:8001

# Fix if needed
echo "REACT_APP_BACKEND_URL=http://192.168.2.26:8001" | sudo tee /app/frontend/.env
```

---

### Issue: Supervisor vs Systemd Conflicts

**Symptoms:**
Services won't start because both supervisor and systemd are trying to manage them.

**Solution:**
Choose ONE method:

**Option 1: Use Supervisor (Development)**
```bash
# Stop systemd services
sudo systemctl stop tactical-backend tactical-frontend
sudo systemctl disable tactical-backend tactical-frontend

# Use supervisor
sudo supervisorctl start backend frontend
sudo supervisorctl status
```

**Option 2: Use Systemd (Production)**
```bash
# Stop supervisor
sudo supervisorctl stop all
sudo systemctl stop supervisor

# Use systemd
sudo systemctl start tactical-backend tactical-frontend
sudo systemctl enable tactical-backend tactical-frontend
```

---

## Network & Access Issues

### Issue: Cannot Access Panel from Browser

**Symptoms:**
- `http://localhost:3000` - Connection refused
- `http://192.168.2.26:3000` - Timeout or connection refused

**Diagnosis Checklist:**

**1. Are Services Running?**
```bash
# Check status
sudo systemctl status tactical-frontend tactical-backend
# OR
sudo supervisorctl status

# Should show: RUNNING
```

**2. Are Services Listening on Correct Interface?**
```bash
# Check what's listening
netstat -tlnp | grep -E ":3000|:8001"
ss -tlnp | grep -E ":3000|:8001"

# Should show:
# 0.0.0.0:3000 (NOT 127.0.0.1:3000)
# 0.0.0.0:8001 (NOT 127.0.0.1:8001)
```

**Fix if showing 127.0.0.1:**
```bash
# For systemd:
sudo nano /etc/systemd/system/tactical-frontend.service
# Add: Environment="HOST=0.0.0.0"

sudo systemctl daemon-reload
sudo systemctl restart tactical-frontend

# For supervisor:
sudo nano /etc/supervisor/conf.d/supervisord.conf
# Ensure: environment=HOST="0.0.0.0",PORT="3000"

sudo supervisorctl restart frontend
```

**3. Is Firewall Blocking?**
```bash
# Check UFW status
sudo ufw status

# Check iptables
sudo iptables -L -n | grep -E "3000|8001"

# Open ports if needed
sudo ufw allow 3000/tcp
sudo ufw allow 8001/tcp

# Or use installer
cd /app/scripts
sudo bash ./install.sh
# Select Option 4: Configure Firewall
```

**4. Test Connectivity**
```bash
# From server itself
curl http://localhost:3000
curl http://127.0.0.1:3000

# From server using its IP
curl http://192.168.2.26:3000

# From another machine
telnet 192.168.2.26 3000
nc -zv 192.168.2.26 3000
```

---

### Issue: Wrong IP Address

**Symptoms:**
Trying to access but getting connection refused.

**Solution:**
Find your actual IP:
```bash
# Show all IPs
hostname -I
ip addr show

# Common interfaces:
ip addr show eth0
ip addr show ens33
```

Use the correct IP in your browser:
```
http://YOUR_ACTUAL_IP:3000
```

---

### Issue: CORS Errors in Browser Console

**Symptoms:**
```
Access to XMLHttpRequest at 'http://...' from origin 'http://...' has been blocked by CORS policy
```

**Solution:**
```bash
# Check backend .env
cat /app/backend/.env

# Should have:
CORS_ORIGINS="*"

# Or specific origins:
CORS_ORIGINS="http://192.168.2.26:3000,http://localhost:3000"

# Restart backend
sudo systemctl restart tactical-backend
# OR
sudo supervisorctl restart backend
```

---

## Database Connection Issues

### Issue: "Could not connect to MongoDB"

**Diagnosis:**
```bash
# Check MongoDB status
sudo systemctl status mongodb
# OR
sudo systemctl status mongod

# Test connection
mongosh --eval "db.version()"
```

**Solutions:**

**1. MongoDB Not Running**
```bash
sudo systemctl start mongodb
sudo systemctl enable mongodb
sudo systemctl status mongodb
```

**2. Wrong MongoDB URL**
```bash
# Check backend .env
cat /app/backend/.env

# Should have:
MONGO_URL="mongodb://localhost:27017"
DB_NAME="test_database"

# Update if wrong
echo 'MONGO_URL="mongodb://localhost:27017"' | sudo tee -a /app/backend/.env
echo 'DB_NAME="tactical_panel"' | sudo tee -a /app/backend/.env
```

**3. MongoDB Not Installed**
```bash
# Ubuntu/Debian
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org
sudo systemctl start mongod
sudo systemctl enable mongod
```

**4. MongoDB Port Conflict**
```bash
# Check if something is using port 27017
sudo lsof -i :27017

# Stop conflicting service or change MongoDB port
sudo nano /etc/mongod.conf
# Change: port: 27018

sudo systemctl restart mongod

# Update .env
echo 'MONGO_URL="mongodb://localhost:27018"' | sudo tee /app/backend/.env
```

---

## Permission Errors

### Issue: "EACCES: permission denied"

**Symptoms:**
```
Error: EACCES: permission denied, open '/app/...'
```

**Solution:**
```bash
# Fix all permissions
cd /app/scripts
sudo bash ./fix-permissions.sh

# Or manually
sudo chown -R $USER:$USER /app
chmod -R 755 /app

# Specific directories
sudo chown -R $USER:$USER /tmp/arma_servers
chmod -R 755 /tmp/arma_servers
```

---

### Issue: Cannot Write to Log Files

**Solution:**
```bash
# Create log directory
sudo mkdir -p /var/log/tactical
sudo chown -R $USER:$USER /var/log/tactical

# Or use /tmp
sudo mkdir -p /tmp/tactical-logs
chmod 777 /tmp/tactical-logs
```

---

## Frontend Issues

### Issue: "Blank Page" or "White Screen"

**Diagnosis:**
```bash
# Check browser console (F12) for errors
# Check frontend logs
sudo journalctl -u tactical-frontend -f
# OR
tail -f /var/log/supervisor/frontend.err.log
```

**Common Causes:**

**1. Build Errors**
```bash
cd /app/frontend
yarn install
yarn build
```

**2. API URL Wrong**
```bash
# Check .env
cat /app/frontend/.env

# Should have correct backend URL:
REACT_APP_BACKEND_URL=http://192.168.2.26:8001

# Update and restart
sudo systemctl restart tactical-frontend
```

**3. Missing Dependencies**
```bash
cd /app/frontend
rm -rf node_modules
yarn install
```

---

### Issue: "Failed to fetch" or API Errors

**Symptoms:**
Browser console shows:
```
Failed to fetch
TypeError: NetworkError when attempting to fetch resource
```

**Solutions:**

**1. Backend Not Running**
```bash
sudo systemctl start tactical-backend
```

**2. Wrong API URL**
```bash
# Check in browser console what URL it's trying to reach
# Update frontend .env
echo "REACT_APP_BACKEND_URL=http://correct-ip:8001" | sudo tee /app/frontend/.env
sudo systemctl restart tactical-frontend
```

**3. CORS Issue**
See CORS section above

---

## Backend API Issues

### Issue: 401 Unauthorized on All Requests

**Symptoms:**
All API calls return 401 even with valid credentials

**Solutions:**

**1. Check JWT Secret**
```bash
cat /app/backend/.env | grep SECRET_KEY

# Should have a long random string
# If missing, add one:
echo "SECRET_KEY=$(openssl rand -hex 32)" | sudo tee -a /app/backend/.env
sudo systemctl restart tactical-backend
```

**2. Token Expired**
```bash
# Clear browser storage and login again
# In browser console (F12):
localStorage.clear()
# Reload page and login
```

---

### Issue: 500 Internal Server Error

**Diagnosis:**
```bash
# Check backend logs
sudo journalctl -u tactical-backend -f
# OR
tail -f /var/log/supervisor/backend.err.log

# Look for Python tracebacks
```

**Common Causes:**

**1. Database Error**
Check MongoDB connection (see database section)

**2. Missing Environment Variables**
```bash
cat /app/backend/.env

# Required variables:
MONGO_URL
DB_NAME
SECRET_KEY
CORS_ORIGINS
```

**3. Python Import Errors**
```bash
cd /app/backend
source venv/bin/activate
python -c "import server"
# Check for any import errors
```

---

## Firewall Configuration

### Issue: Firewall Blocking Connections

**UFW Commands:**
```bash
# Check status
sudo ufw status verbose

# Allow ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 3000/tcp  # Frontend
sudo ufw allow 8001/tcp  # Backend
sudo ufw allow 2001:2100/tcp  # Game servers
sudo ufw allow 2001:2100/udp  # Game servers

# Enable IPv6
sudo sed -i 's/IPV6=no/IPV6=yes/' /etc/default/ufw

# Enable firewall
sudo ufw enable

# Or use installer
cd /app/scripts
sudo bash ./install.sh
# Option 4: Configure Firewall
```

**iptables Commands:**
```bash
# Check rules
sudo iptables -L -n

# Allow ports
sudo iptables -A INPUT -p tcp --dport 3000 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8001 -j ACCEPT

# Save rules (Ubuntu/Debian)
sudo netfilter-persistent save

# Save rules (RHEL/CentOS)
sudo service iptables save
```

---

## Performance Issues

### Issue: High CPU Usage

**Diagnosis:**
```bash
# Check processes
top
htop

# Check specific services
systemctl status tactical-backend
systemctl status tactical-frontend
```

**Solutions:**

**1. Frontend Hot Reload**
In development, React's hot reload can use CPU. This is normal.

**2. Backend Workers**
```bash
# Reduce uvicorn workers
sudo nano /etc/systemd/system/tactical-backend.service

# Change --workers=4 to --workers=1
ExecStart=...uvicorn server:app --host 0.0.0.0 --port 8001 --workers 1

sudo systemctl daemon-reload
sudo systemctl restart tactical-backend
```

---

### Issue: High Memory Usage

**Solution:**
```bash
# Check memory
free -h

# Restart services to clear memory
sudo systemctl restart tactical-backend tactical-frontend

# Or use supervisor
sudo supervisorctl restart all
```

---

## Common Error Messages

### "MODULE_NOT_FOUND" (Frontend)

**Solution:**
```bash
cd /app/frontend
rm -rf node_modules package-lock.json yarn.lock
yarn install
```

### "ModuleNotFoundError" (Backend)

**Solution:**
```bash
cd /app/backend
source venv/bin/activate
pip install -r requirements.txt
deactivate
sudo systemctl restart tactical-backend
```

### "Address already in use"

**Solution:**
```bash
# Find and kill process
sudo lsof -i :3000  # or :8001
sudo kill -9 <PID>

# Restart service
sudo systemctl restart tactical-frontend  # or tactical-backend
```

### "Cannot connect to MongoDB"

See Database Connection Issues section above.

---

## Getting Help

### Collect Diagnostic Information

Run this script to collect all relevant information:

```bash
cat > /tmp/diagnostic.sh << 'EOF'
#!/bin/bash
echo "=== TACTICAL PANEL DIAGNOSTICS ==="
echo ""
echo "=== System Info ==="
uname -a
echo ""
echo "=== IP Addresses ==="
hostname -I
ip addr show
echo ""
echo "=== Service Status ==="
sudo systemctl status tactical-backend --no-pager || echo "Systemd not available"
sudo systemctl status tactical-frontend --no-pager || echo "Systemd not available"
sudo supervisorctl status || echo "Supervisor not available"
echo ""
echo "=== Port Listening ==="
netstat -tlnp | grep -E ":3000|:8001|:27017"
echo ""
echo "=== Firewall Status ==="
sudo ufw status || echo "UFW not installed"
sudo iptables -L -n | head -20 || echo "iptables not available"
echo ""
echo "=== MongoDB Status ==="
sudo systemctl status mongodb --no-pager || sudo systemctl status mongod --no-pager || echo "MongoDB status unknown"
echo ""
echo "=== Disk Space ==="
df -h
echo ""
echo "=== Memory ==="
free -h
echo ""
echo "=== Recent Backend Logs ==="
sudo journalctl -u tactical-backend --no-pager -n 20 || tail -20 /var/log/supervisor/backend.err.log || echo "No backend logs found"
echo ""
echo "=== Recent Frontend Logs ==="
sudo journalctl -u tactical-frontend --no-pager -n 20 || tail -20 /var/log/supervisor/frontend.err.log || echo "No frontend logs found"
EOF

chmod +x /tmp/diagnostic.sh
/tmp/diagnostic.sh > /tmp/panel-diagnostics.txt
cat /tmp/panel-diagnostics.txt
```

Share the output when seeking help.

---

## Quick Reference

### Service Management
```bash
# Systemd
sudo systemctl start|stop|restart|status tactical-backend
sudo systemctl start|stop|restart|status tactical-frontend

# Supervisor
sudo supervisorctl start|stop|restart|status backend
sudo supervisorctl start|stop|restart|status frontend
```

### View Logs
```bash
# Systemd
sudo journalctl -u tactical-backend -f
sudo journalctl -u tactical-frontend -f

# Supervisor
tail -f /var/log/supervisor/backend.err.log
tail -f /var/log/supervisor/frontend.out.log
```

### Test Connectivity
```bash
curl http://localhost:3000
curl http://localhost:8001/api/auth/check-first-run
```

### Update Panel
```bash
cd /app/scripts
sudo bash ./update-panel.sh
```
