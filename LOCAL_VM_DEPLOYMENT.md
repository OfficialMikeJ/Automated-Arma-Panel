# Local VM Deployment Guide

## For Ubuntu Server VM at 192.168.2.26

This guide will help you deploy the Tactical Server Control Panel on your local VM.

---

## Current Environment

You're currently in the **Emergent Cloud Development Environment** where:
- Services run via **Supervisor** (not systemd)
- IP: `10.208.144.125`
- Purpose: Development and testing

## Deploying to Your Local VM (192.168.2.26)

### Option 1: Copy Files to Your VM (Recommended)

#### Step 1: Package the Application

On the Emergent server, create a deployment package:

```bash
cd /app
tar -czf tactical-panel.tar.gz \
  --exclude=node_modules \
  --exclude=backend/venv \
  --exclude=backend/__pycache__ \
  --exclude=.git \
  backend/ frontend/ scripts/ *.md
```

#### Step 2: Transfer to Your VM

```bash
# From your local machine:
scp root@10.208.144.125:/app/tactical-panel.tar.gz ~/
scp tactical-panel.tar.gz mike@192.168.2.26:/home/mike/
```

#### Step 3: Extract and Setup on Your VM

SSH into your VM (192.168.2.26):

```bash
ssh mike@192.168.2.26
cd /home/mike
tar -xzf tactical-panel.tar.gz
sudo mv backend frontend scripts *.md /app/
cd /app
```

#### Step 4: Run the Installer

```bash
cd /app/scripts
sudo bash ./install.sh
```

**Select Option 2:** Native Installation + Guided Setup

The installer will:
- ✅ Auto-install Python 3 and Node.js (if missing)
- ✅ Install MongoDB
- ✅ Create Python virtual environment
- ✅ Install all dependencies
- ✅ Configure services
- ✅ Setup systemd services (corrected paths)

#### Step 5: Configure Firewall (Optional)

```bash
cd /app/scripts
sudo bash ./install.sh
# Select Option 4: Configure Firewall
```

This opens ports: 22, 3000, 8001, 2001-2100

---

### Option 2: Clone from Git (If you have the code in git)

```bash
# On your VM:
git clone <your-repo-url> /app
cd /app/scripts
sudo bash ./install.sh
```

---

## Systemd Service Setup (For Your VM)

### Updated Service Files

The systemd service files have been **fixed** for proper deployment:

**Changes Made:**
- ✅ Changed User from `www-data` to `root` (or your user)
- ✅ Fixed Python virtual environment path: `/root/.venv/bin/uvicorn`
- ✅ Added `HOST=0.0.0.0` for frontend network binding
- ✅ Removed restrictive security settings for development
- ✅ Fixed MongoDB service name dependency

### Manual Systemd Installation (Alternative)

If the installer doesn't set up systemd, do it manually:

```bash
# Copy service files
sudo cp /app/scripts/systemd/tactical-backend.service /etc/systemd/system/
sudo cp /app/scripts/systemd/tactical-frontend.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable tactical-backend
sudo systemctl enable tactical-frontend

# Start services
sudo systemctl start tactical-backend
sudo systemctl start tactical-frontend

# Check status
sudo systemctl status tactical-backend
sudo systemctl status tactical-frontend
```

### View Logs

```bash
# Backend logs
sudo journalctl -u tactical-backend -f

# Frontend logs
sudo journalctl -u tactical-frontend -f
```

---

## Network Access Configuration

### Why You Can't Access from 192.168.2.26

**Problem:** The application is currently running on the Emergent cloud server (`10.208.144.125`), not your local VM (`192.168.2.26`).

**Solution:** Deploy the application TO your VM at 192.168.2.26

### After Deployment to Your VM

#### Test Local Access

```bash
# On your VM (192.168.2.26):
curl http://localhost:3000
curl http://192.168.2.26:3000
```

#### Access from Your Desktop

Open browser on your desktop:
```
http://192.168.2.26:3000
```

#### Firewall Configuration

Make sure ports are open:

```bash
# Check if UFW is active
sudo ufw status

# If active, allow ports:
sudo ufw allow 3000/tcp
sudo ufw allow 8001/tcp

# Or use the installer:
cd /app/scripts
sudo bash ./install.sh
# Select Option 4
```

---

## Troubleshooting

### Issue: "Job for tactical-backend.service failed"

**Causes:**
1. Wrong virtual environment path
2. Wrong user permissions
3. Missing dependencies
4. MongoDB not running

**Solution:**

Check service status:
```bash
sudo systemctl status tactical-backend -l
sudo journalctl -xeu tactical-backend --no-pager
```

Common fixes:

**1. Virtual Environment Path:**
```bash
# Find correct venv path:
find /app -name "uvicorn" -type f 2>/dev/null
find /root -name "uvicorn" -type f 2>/dev/null

# Update service file with correct path
sudo nano /etc/systemd/system/tactical-backend.service
# Change: ExecStart=/correct/path/to/uvicorn

sudo systemctl daemon-reload
sudo systemctl restart tactical-backend
```

**2. User Permissions:**
```bash
# If running as your user (mike):
sudo sed -i 's/User=root/User=mike/g' /etc/systemd/system/tactical-backend.service
sudo sed -i 's/Group=root/Group=mike/g' /etc/systemd/system/tactical-backend.service
sudo sed -i 's/User=root/User=mike/g' /etc/systemd/system/tactical-frontend.service
sudo sed -i 's/Group=root/Group=mike/g' /etc/systemd/system/tactical-frontend.service

sudo systemctl daemon-reload
sudo systemctl restart tactical-backend tactical-frontend
```

**3. MongoDB Not Running:**
```bash
sudo systemctl status mongodb  # or mongod
sudo systemctl start mongodb   # or mongod
sudo systemctl enable mongodb
```

**4. Dependencies Missing:**
```bash
# Backend:
cd /app/backend
source venv/bin/activate  # or /root/.venv/bin/activate
pip install -r requirements.txt

# Frontend:
cd /app/frontend
yarn install
```

### Issue: Can't Access from Network

**Check Binding:**
```bash
# Should show 0.0.0.0:3000 and 0.0.0.0:8001
netstat -tlnp | grep -E ":3000|:8001"
```

**Fix Frontend Binding:**
```bash
# Edit service file:
sudo nano /etc/systemd/system/tactical-frontend.service

# Ensure this line exists:
Environment="HOST=0.0.0.0"

sudo systemctl daemon-reload
sudo systemctl restart tactical-frontend
```

### Issue: Ports Already in Use

```bash
# Find what's using port 3000:
sudo lsof -i :3000
sudo lsof -i :8001

# Kill the process:
sudo kill -9 <PID>

# Or use the port:
sudo systemctl stop tactical-frontend
sudo systemctl stop tactical-backend
```

---

## Quick Start Commands for Your VM

Once deployed to your VM (192.168.2.26):

### Check Service Status
```bash
sudo systemctl status tactical-backend
sudo systemctl status tactical-frontend
```

### Restart Services
```bash
sudo systemctl restart tactical-backend
sudo systemctl restart tactical-frontend
```

### View Logs
```bash
sudo journalctl -u tactical-backend -f
sudo journalctl -u tactical-frontend -f
```

### Update Panel
```bash
cd /app/scripts
sudo bash ./update-panel.sh
```

### Access Panel
```
http://192.168.2.26:3000
```

---

## Complete Deployment Checklist

For your local VM at 192.168.2.26:

- [ ] Transfer files from Emergent server to your VM
- [ ] Extract to `/app` directory
- [ ] Run installer: `sudo bash /app/scripts/install.sh`
- [ ] Select Option 2: Native Installation
- [ ] Installer auto-installs dependencies
- [ ] Installer sets up systemd services
- [ ] Configure firewall (Option 4)
- [ ] Start services: `sudo systemctl start tactical-backend tactical-frontend`
- [ ] Test access: `http://192.168.2.26:3000`
- [ ] Complete first-time setup
- [ ] Configure sub-admins (if needed)

---

## Network Diagram

```
[Your Desktop] 
    ↓
    ↓ http://192.168.2.26:3000
    ↓
[Your Local VM] (192.168.2.26)
    ├── Frontend: 0.0.0.0:3000
    ├── Backend: 0.0.0.0:8001
    └── MongoDB: 127.0.0.1:27017

[Emergent Cloud] (10.208.144.125)
    ├── Development Environment
    ├── Testing
    └── Package Creation
```

---

## Support

If you encounter issues:

1. Check service logs:
   ```bash
   sudo journalctl -xeu tactical-backend --no-pager | tail -100
   sudo journalctl -xeu tactical-frontend --no-pager | tail -100
   ```

2. Verify network binding:
   ```bash
   netstat -tlnp | grep -E ":3000|:8001"
   ```

3. Test connectivity:
   ```bash
   curl http://localhost:3000
   curl http://192.168.2.26:3000
   ```

4. Check MongoDB:
   ```bash
   sudo systemctl status mongodb
   mongosh --eval "db.version()"
   ```

The fixed systemd service files are ready for deployment to your VM!
