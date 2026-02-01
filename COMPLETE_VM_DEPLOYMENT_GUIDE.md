# Complete VM Deployment Guide for Tactical Reforger Control Panel

## 🎯 Critical Information - READ THIS FIRST

You are currently looking at code running in the **Emergent Cloud Development Environment**.  
This is NOT your VM at `192.168.2.26` - this is a remote cloud container used for development.

To run the panel on YOUR Ubuntu Server VM, you need to **deploy this code** to your machine.

---

## 📋 Prerequisites

Your Ubuntu Server VM should have:
- Ubuntu 20.04 or 22.04 LTS
- At least 4GB RAM
- 20GB free disk space
- Root or sudo access
- Network connectivity

---

## 🚀 Deployment Methods

### Method 1: Direct Installation (Recommended)

#### Step 1: Download the Code

On your VM (192.168.2.26), download the code:

```bash
# If you have git repository
cd /opt
sudo git clone <your-repo-url> tactical-panel
cd tactical-panel

# OR if you're copying from the Emergent environment
# (see "Copying from Emergent" section below)
```

#### Step 2: Run the Installer

```bash
cd /opt/tactical-panel/scripts
sudo bash ./install.sh
```

**Important**: Always use `sudo bash ./install.sh` - never just `./install.sh`

#### Step 3: Choose Installation Option

The installer will present you with a menu. Select **Option 2: Native Installation**

The installer will automatically:
- ✅ Detect and install missing dependencies (Python 3, Node.js, MongoDB)
- ✅ Create Python virtual environment at `/root/.venv`
- ✅ Install all Python packages
- ✅ Install all Node.js packages via yarn
- ✅ Configure MongoDB database
- ✅ Setup systemd services for auto-start
- ✅ Configure proper permissions

#### Step 4: Configure Firewall (Recommended)

After installation completes, run the installer again:

```bash
sudo bash ./install.sh
```

Select **Option 4: Configure Firewall**

This will:
- Install and enable UFW (if not already installed)
- Open port 22 (SSH)
- Open port 3000 (Web UI)
- Open port 8001 (Backend API)
- Open ports 2001-2100 (Arma server ports)

#### Step 5: Start Services

The installer sets up systemd services that start automatically:

```bash
# Check service status
sudo systemctl status tactical-backend
sudo systemctl status tactical-frontend

# If services are not running, start them:
sudo systemctl start tactical-backend
sudo systemctl start tactical-frontend

# Enable auto-start on boot:
sudo systemctl enable tactical-backend
sudo systemctl enable tactical-frontend
```

#### Step 6: Access the Panel

Open your browser and navigate to:
- **From the VM itself**: http://localhost:3000
- **From your network**: http://192.168.2.26:3000

You should see the Tactical Command login page.

---

### Method 2: Copying from Emergent Environment

If you need to copy files from the Emergent development environment to your VM:

#### On Emergent Server:

```bash
cd /app
tar -czf tactical-panel.tar.gz \
  --exclude=node_modules \
  --exclude=backend/venv \
  --exclude=backend/__pycache__ \
  --exclude=.git \
  --exclude=*.pyc \
  backend/ frontend/ scripts/ *.md *.sh
```

#### Transfer to Your Local Machine:

```bash
# From your local machine (laptop/desktop):
scp root@<emergent-ip>:/app/tactical-panel.tar.gz ~/tactical-panel.tar.gz
```

#### Transfer to Your VM:

```bash
# From your local machine:
scp ~/tactical-panel.tar.gz mike@192.168.2.26:/home/mike/
```

#### On Your VM:

```bash
ssh mike@192.168.2.26
cd /home/mike
sudo mkdir -p /opt/tactical-panel
sudo tar -xzf tactical-panel.tar.gz -C /opt/tactical-panel
cd /opt/tactical-panel/scripts
sudo bash ./install.sh
```

---

## 🔍 Troubleshooting

### Issue 1: Cannot Access Web Panel

**Symptom**: Browser shows "This site can't be reached" or connection timeout

**Solutions**:

1. **Check if services are running**:
```bash
sudo systemctl status tactical-frontend
sudo systemctl status tactical-backend
```

If not running:
```bash
sudo systemctl start tactical-frontend
sudo systemctl start tactical-backend
```

2. **Check if ports are listening**:
```bash
sudo ss -tuln | grep -E '3000|8001'
```

You should see:
```
tcp   LISTEN 0.0.0.0:3000
tcp   LISTEN 0.0.0.0:8001
```

3. **Check firewall**:
```bash
sudo ufw status
```

If UFW is active and blocking:
```bash
sudo ufw allow 3000/tcp
sudo ufw allow 8001/tcp
```

4. **Test locally first**:
```bash
curl http://127.0.0.1:3000
curl http://127.0.0.1:8001/api/health
```

If these work but http://192.168.2.26:3000 doesn't, it's a network/firewall issue.

5. **Check service logs**:
```bash
sudo journalctl -u tactical-frontend -n 50 --no-pager
sudo journalctl -u tactical-backend -n 50 --no-pager
```

### Issue 2: Systemd Service Fails to Start

**Symptom**: `systemctl status` shows failed or inactive state

**Solutions**:

1. **Check detailed error logs**:
```bash
sudo journalctl -xeu tactical-backend
sudo journalctl -xeu tactical-frontend
```

2. **Verify paths in service files**:
```bash
cat /etc/systemd/system/tactical-backend.service
cat /etc/systemd/system/tactical-frontend.service
```

Ensure paths match your installation:
- Python venv: `/root/.venv/bin/python3`
- Application path: `/opt/tactical-panel`

3. **Verify virtual environment exists**:
```bash
ls -la /root/.venv/bin/python3
```

If missing, recreate:
```bash
cd /opt/tactical-panel/backend
python3 -m venv /root/.venv
source /root/.venv/bin/activate
pip install -r requirements.txt
```

4. **Reload systemd after changes**:
```bash
sudo systemctl daemon-reload
sudo systemctl restart tactical-backend
sudo systemctl restart tactical-frontend
```

### Issue 3: MongoDB Connection Error

**Symptom**: Backend logs show "Connection refused" or MongoDB errors

**Solutions**:

1. **Check if MongoDB is running**:
```bash
sudo systemctl status mongod
```

2. **Start MongoDB if not running**:
```bash
sudo systemctl start mongod
sudo systemctl enable mongod
```

3. **Verify MongoDB connection**:
```bash
mongosh --eval "db.runCommand({ connectionStatus: 1 })"
```

4. **Check backend .env file**:
```bash
cat /opt/tactical-panel/backend/.env
```

Should contain:
```
MONGO_URL=mongodb://localhost:27017/tactical_panel
DB_NAME=tactical_panel
```

### Issue 4: Frontend Shows Blank Page

**Symptom**: Page loads but is completely blank or shows errors in browser console

**Solutions**:

1. **Check browser console** (F12 in most browsers):
   - Look for CORS errors
   - Look for 404 errors on API calls

2. **Verify backend URL in frontend .env**:
```bash
cat /opt/tactical-panel/frontend/.env
```

Should contain:
```
REACT_APP_BACKEND_URL=http://192.168.2.26:8001
```

**Important**: Update this to match your VM's IP address!

3. **Rebuild frontend if needed**:
```bash
cd /opt/tactical-panel/frontend
yarn build
sudo systemctl restart tactical-frontend
```

### Issue 5: Permission Denied Errors

**Symptom**: Services fail with permission errors

**Solutions**:

1. **Fix ownership**:
```bash
sudo chown -R root:root /opt/tactical-panel
sudo chmod +x /opt/tactical-panel/scripts/*.sh
```

2. **Run installer fix-permissions option**:
```bash
cd /opt/tactical-panel/scripts
sudo bash ./install.sh
# Select option to fix permissions
```

---

## 🔒 Security Considerations

### 1. Change Default Ports (Optional but Recommended)

**Frontend Port** (default: 3000):
Edit `/etc/systemd/system/tactical-frontend.service`:
```ini
Environment="PORT=8080"
```

Update frontend .env:
```
PORT=8080
```

**Backend Port** (default: 8001):
Edit `/etc/systemd/system/tactical-backend.service` and backend .env

Don't forget to update firewall rules!

### 2. Enable HTTPS (Recommended for Production)

Use nginx as a reverse proxy with Let's Encrypt SSL:

```bash
sudo apt install nginx certbot python3-certbot-nginx
```

See `PRODUCTION_DEPLOYMENT.md` for detailed HTTPS setup.

### 3. Secure MongoDB

```bash
# Enable MongoDB authentication
sudo nano /etc/mongod.conf

# Add under security:
security:
  authorization: enabled
```

Create admin user and update .env with credentials.

### 4. Regular Updates

```bash
cd /opt/tactical-panel/scripts
sudo bash ./install.sh
# Select "Update Panel" option
```

---

## 📊 Verifying Installation Success

### Quick Test Checklist:

1. ✅ Services running: `sudo systemctl status tactical-backend tactical-frontend`
2. ✅ Ports listening: `sudo ss -tuln | grep -E '3000|8001'`
3. ✅ Backend health: `curl http://localhost:8001/api/health`
4. ✅ Frontend loads: `curl http://localhost:3000`
5. ✅ Remote access: Open http://192.168.2.26:3000 in browser
6. ✅ Login page visible
7. ✅ Can create admin account

---

## 🔄 Updating the Panel

To update to the latest version:

```bash
cd /opt/tactical-panel

# If using git:
sudo git pull

# Re-run installer:
cd scripts
sudo bash ./install.sh
# Select "Update Panel" option
```

The update process will:
- Pull latest code changes
- Update dependencies
- Restart services
- Preserve your database and configuration

---

## 🆘 Getting Help

If you encounter issues not covered here:

1. **Check all log files**:
```bash
sudo journalctl -u tactical-backend -n 100
sudo journalctl -u tactical-frontend -n 100
```

2. **Verify network connectivity**:
```bash
ping 192.168.2.26
curl -v http://192.168.2.26:3000
```

3. **Check comprehensive troubleshooting guide**:
See `TROUBLESHOOTING_COMPLETE.md` in the project root

4. **Review installation logs**:
```bash
cat /opt/tactical-panel/install.log
```

---

## 📁 Important File Locations

After installation, key files will be at:

- **Application**: `/opt/tactical-panel/`
- **Python venv**: `/root/.venv/`
- **Systemd services**: `/etc/systemd/system/tactical-*.service`
- **MongoDB data**: `/var/lib/mongodb/`
- **Application logs**: `/var/log/tactical/`
- **Systemd logs**: `journalctl -u tactical-backend` or `tactical-frontend`

---

## 🎮 Next Steps After Installation

1. **Create your admin account** via the web UI
2. **Install SteamCMD** (if you want to download Arma servers)
3. **Add your first server instance**
4. **Configure firewall rules for server ports**
5. **Set up sub-admin users** (if needed)
6. **Configure resource allocation** per server

---

## ⚠️ Common Mistakes to Avoid

1. ❌ Running installer without `sudo`
2. ❌ Trying to access the Emergent cloud IP instead of your VM IP
3. ❌ Not updating `REACT_APP_BACKEND_URL` in frontend .env
4. ❌ Forgetting to open firewall ports
5. ❌ Using npm instead of yarn
6. ❌ Not enabling systemd services (they won't auto-start on reboot)

---

## 🎯 Summary

**To deploy on YOUR VM (192.168.2.26):**

1. Get the code onto your VM
2. Run `sudo bash ./install.sh` from `/scripts` directory
3. Choose Native Installation
4. Configure firewall
5. Start/verify services
6. Access at http://192.168.2.26:3000

**You are NOT deploying to the Emergent environment - that's just for development!**
