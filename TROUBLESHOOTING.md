# Troubleshooting Guide - Tactical Command

Common issues and solutions for Ubuntu Server LTS 24.04

## Permission Issues

### Problem: "Permission denied" when running scripts

**Symptoms:**
```bash
./install.sh
-bash: ./install.sh: Permission denied
```

**Solution 1: Quick Fix (Recommended)**
```bash
cd /app/scripts
sudo ./fix-permissions.sh
```

**Solution 2: Manual Fix**
```bash
# Fix ownership
sudo chown -R $USER:$USER /app

# Make scripts executable
chmod +x /app/scripts/*.sh

# Try again
./install.sh
```

**Why this happens:**
- Files were created by root user
- Current user doesn't have execute permissions

---

### Problem: "Permission denied" accessing /tmp/arma_servers

**Solution:**
```bash
sudo mkdir -p /tmp/arma_servers
sudo chown -R $USER:$USER /tmp/arma_servers
chmod -R 755 /tmp/arma_servers
```

---

## Installation Issues

### Problem: MongoDB won't install

**Symptoms:**
```
E: Unable to locate package mongodb-org
```

**Solution:**
```bash
# Add MongoDB repository
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu $(lsb_release -cs)/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Update and install
sudo apt-get update
sudo apt-get install -y mongodb-org

# Start service
sudo systemctl start mongod
sudo systemctl enable mongod
```

---

### Problem: Python version too old

**Symptoms:**
```
Python 3.10.x found, but 3.11+ required
```

**Solution for Ubuntu 24.04:**
```bash
# Add deadsnakes PPA
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update

# Install Python 3.11
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev

# Verify
python3.11 --version
```

---

### Problem: Node.js version too old

**Solution:**
```bash
# Install latest Node.js LTS
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify
node --version  # Should be v18.x or higher
```

---

### Problem: Yarn not installing

**Solution:**
```bash
# Install via npm
sudo npm install -g yarn

# Verify
yarn --version
```

---

## Docker Issues

### Problem: Docker permission denied

**Symptoms:**
```
permission denied while trying to connect to Docker daemon
```

**Solution:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in, or run:
newgrp docker

# Test
docker ps
```

---

### Problem: Docker Compose not found

**Solution:**
```bash
# Download latest version
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make executable
sudo chmod +x /usr/local/bin/docker-compose

# Verify
docker-compose --version
```

---

## Runtime Issues

### Problem: Backend won't start

**Check logs:**
```bash
# If using supervisor
tail -50 /var/log/supervisor/backend.err.log

# If using systemd
sudo journalctl -u tactical-backend -n 50

# If running manually
cd /app/backend
source venv/bin/activate
uvicorn server:app --host 0.0.0.0 --port 8001
```

**Common causes:**
1. **MongoDB not running**
   ```bash
   sudo systemctl status mongod
   sudo systemctl start mongod
   ```

2. **Port 8001 already in use**
   ```bash
   sudo lsof -i :8001
   # Kill the process if needed
   ```

3. **Missing Python packages**
   ```bash
   cd /app/backend
   source venv/bin/activate
   pip install -r requirements.txt
   ```

---

### Problem: Frontend won't start

**Check logs:**
```bash
# If using supervisor
tail -50 /var/log/supervisor/frontend.err.log

# If using systemd
sudo journalctl -u tactical-frontend -n 50
```

**Common causes:**
1. **Port 3000 already in use**
   ```bash
   sudo lsof -i :3000
   ```

2. **Missing node_modules**
   ```bash
   cd /app/frontend
   yarn install
   ```

3. **Build errors**
   ```bash
   cd /app/frontend
   yarn build
   ```

---

### Problem: "Cannot connect to backend"

**Check backend URL:**
```bash
# Verify environment variable
cat /app/frontend/.env | grep REACT_APP_BACKEND_URL

# Should be:
# REACT_APP_BACKEND_URL=http://localhost:8001
# or your server's URL
```

**Test backend directly:**
```bash
curl http://localhost:8001/api/auth/check-first-run
```

---

### Problem: SteamCMD not found when starting server

**Solution:**
```bash
# Install SteamCMD manually
mkdir -p ~/steamcmd
cd ~/steamcmd
wget https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz
tar -xzf steamcmd_linux.tar.gz
rm steamcmd_linux.tar.gz
chmod +x steamcmd.sh

# Run initial update
./steamcmd.sh +quit

# Verify
ls -la ~/steamcmd/steamcmd.sh
```

---

## Database Issues

### Problem: MongoDB connection refused

**Check MongoDB status:**
```bash
sudo systemctl status mongod
```

**Check MongoDB logs:**
```bash
sudo tail -50 /var/log/mongodb/mongod.log
```

**Restart MongoDB:**
```bash
sudo systemctl restart mongod
```

**Check connection:**
```bash
mongosh --eval "db.adminCommand('ping')"
```

---

### Problem: Database authentication failed

**Reset MongoDB (DEV ONLY):**
```bash
# Stop MongoDB
sudo systemctl stop mongod

# Remove auth requirement temporarily
sudo sed -i 's/^  authorization: enabled/  #authorization: enabled/' /etc/mongod.conf

# Start MongoDB
sudo systemctl start mongod

# Update .env to remove authentication
```

---

## SSL/HTTPS Issues

### Problem: Let's Encrypt fails

**Common causes:**

1. **Domain not pointing to server**
   ```bash
   # Check DNS
   nslookup yourdomain.com
   dig yourdomain.com
   ```

2. **Ports not open**
   ```bash
   # Check firewall
   sudo ufw status
   
   # Open required ports
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   ```

3. **Nginx not running**
   ```bash
   sudo systemctl status nginx
   sudo systemctl start nginx
   ```

---

## Service Management

### Problem: Services not starting on boot

**Enable services:**
```bash
# Systemd
sudo systemctl enable tactical-backend
sudo systemctl enable tactical-frontend

# Check status
sudo systemctl status tactical-backend
sudo systemctl status tactical-frontend
```

---

### Problem: Service won't restart

**Force restart:**
```bash
# Stop service
sudo systemctl stop tactical-backend

# Kill any remaining processes
sudo pkill -f uvicorn

# Start service
sudo systemctl start tactical-backend
```

---

## Network Issues

### Problem: Cannot access panel from other computers

**Check firewall:**
```bash
# Allow ports
sudo ufw allow 3000/tcp  # Frontend
sudo ufw allow 8001/tcp  # Backend (if accessing directly)

# Or allow from specific IP
sudo ufw allow from 192.168.1.0/24 to any port 3000
```

**Check if service is listening:**
```bash
sudo netstat -tlnp | grep 3000
sudo netstat -tlnp | grep 8001
```

---

## Performance Issues

### Problem: High CPU usage

**Check processes:**
```bash
htop
# Look for uvicorn, node, or mongod processes
```

**Check MongoDB performance:**
```bash
mongosh
> db.serverStatus()
```

---

### Problem: High memory usage

**Check memory:**
```bash
free -h
```

**Adjust resource limits:**

Edit service files:
```bash
sudo nano /etc/systemd/system/tactical-backend.service
```

Add:
```ini
[Service]
MemoryLimit=1G
CPUQuota=100%
```

Reload:
```bash
sudo systemctl daemon-reload
sudo systemctl restart tactical-backend
```

---

## Recovery Procedures

### Complete Reinstall

**Backup first:**
```bash
cd /app/scripts
./backup.sh full-backup-$(date +%Y%m%d)
```

**Remove and reinstall:**
```bash
# Stop services
sudo systemctl stop tactical-backend tactical-frontend

# Remove installation (keeps backups)
rm -rf /app/backend/venv
rm -rf /app/frontend/node_modules

# Reinstall
cd /app/scripts
./install.sh --auto
```

---

### Restore from Backup

```bash
cd /app/scripts
./restore.sh backup_20240131_120000
```

---

## Getting Help

### Collect Debug Information

```bash
# Create debug report
cat > debug-info.txt << EOF
=== System Info ===
$(uname -a)
$(lsb_release -a)

=== Services ===
$(sudo systemctl status tactical-backend --no-pager)
$(sudo systemctl status tactical-frontend --no-pager)
$(sudo systemctl status mongod --no-pager)

=== Ports ===
$(sudo netstat -tlnp | grep -E '3000|8001|27017')

=== Recent Logs ===
$(sudo journalctl -u tactical-backend -n 20 --no-pager)

=== Disk Space ===
$(df -h)

=== Memory ===
$(free -h)
EOF

cat debug-info.txt
```

### Check Configuration

```bash
# Backend config
cat /app/backend/.env

# Frontend config
cat /app/frontend/.env

# Verify file permissions
ls -la /app/scripts/
ls -la /app/backend/
ls -la /app/frontend/
```

---

## Quick Reference Commands

```bash
# Fix permissions
sudo /app/scripts/fix-permissions.sh

# View logs
sudo journalctl -u tactical-backend -f
sudo journalctl -u tactical-frontend -f

# Restart services
sudo systemctl restart tactical-backend tactical-frontend

# Check status
sudo systemctl status tactical-backend
sudo systemctl status tactical-frontend

# MongoDB
sudo systemctl status mongod
mongosh

# Docker
docker-compose logs -f
docker-compose restart

# Backup
cd /app/scripts && ./backup.sh

# Restore
cd /app/scripts && ./restore.sh <backup-name>
```

---

## Still Having Issues?

1. Check the installation log: `/app/install.log`
2. Review README.md for requirements
3. Try the automatic permission fix first
4. Collect debug information (see above)
5. Open an issue on GitHub with debug info

---

**Most Common Solutions:**
1. Run `sudo ./fix-permissions.sh` - Fixes 90% of issues
2. Restart services - Fixes running issues
3. Check MongoDB is running - Required for backend
4. Verify firewall allows ports - Required for network access
