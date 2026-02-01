# Complete Fresh Reinstall Guide

## Step 1: Clean Up Current Installation

Run these commands to remove everything:

```bash
# Stop services
sudo systemctl stop tactical-backend tactical-frontend

# Disable services
sudo systemctl disable tactical-backend tactical-frontend

# Remove service files
sudo rm -f /etc/systemd/system/tactical-backend.service
sudo rm -f /etc/systemd/system/tactical-frontend.service

# Reload systemd
sudo systemctl daemon-reload

# Remove installation directory
sudo rm -rf /opt/Automated-Arma-Panel-main

# Optional: Remove MongoDB data (if you want completely fresh)
# sudo systemctl stop mongod
# sudo rm -rf /var/lib/mongodb/*
# sudo systemctl start mongod
```

---

## Step 2: Download Updated Files from Emergent

**Using WinSCP:**
1. Connect to Emergent server
2. Navigate to `/app/`
3. Download the entire project folder to your local computer
4. Disconnect from Emergent

---

## Step 3: Upload to Your VM

**Using WinSCP:**
1. Connect to your VM (192.168.2.26) as user `mike`
2. Navigate to `/home/mike/`
3. Upload the entire project folder
4. Rename it to `Automated-Arma-Panel-main`

---

## Step 4: Move to /opt and Set Permissions

**In SSH terminal:**
```bash
# Move to /opt
sudo mv /home/mike/Automated-Arma-Panel-main /opt/

# Set ownership
sudo chown -R root:root /opt/Automated-Arma-Panel-main

# Make scripts executable
sudo chmod +x /opt/Automated-Arma-Panel-main/scripts/*.sh
```

---

## Step 5: Run the Installer

```bash
cd /opt/Automated-Arma-Panel-main/scripts
sudo bash ./install.sh
```

**Select Option 2: Native Installation**

The installer will now:
- ✅ Auto-detect and install python3-venv
- ✅ Detect Node.js version and upgrade to 20.x if needed
- ✅ Handle emergentintegrations (will ask you)
- ✅ Create proper virtual environment
- ✅ Install all dependencies
- ✅ Verify critical packages
- ✅ Check MongoDB is running
- ✅ Run final verification
- ✅ Create systemd services with correct paths

---

## Step 6: Configure Firewall (Optional)

After installation completes:

```bash
cd /opt/Automated-Arma-Panel-main/scripts
sudo bash ./install.sh
```

**Select Option 4: Configure Firewall**

This will open ports 3000, 8001, and server ports.

---

## Step 7: Verify Installation

```bash
# Check services
sudo systemctl status tactical-backend
sudo systemctl status tactical-frontend

# Both should show "active (running)" in green

# Check ports
sudo ss -tuln | grep -E '3000|8001'

# Test backend
curl http://localhost:8001/api/auth/check-first-run

# Test frontend
curl -I http://localhost:3000
```

---

## Step 8: Access Panel

Open browser: **http://192.168.2.26:3000**

You should see the login page and be able to create an admin account!

---

## If You Encounter Issues

Run the diagnostic tool:

```bash
cd /opt/Automated-Arma-Panel-main/scripts
sudo bash ./diagnose-and-fix.sh
```

It will automatically check everything and offer to fix problems.

---

## What's Different This Time

All the issues you encountered have been fixed in the updated installer:

✅ python3-venv auto-installs  
✅ Node.js auto-upgrades to 20.x  
✅ emergentintegrations handled properly  
✅ uvicorn verified before finishing  
✅ Systemd services use correct paths  
✅ Final verification ensures everything works  

---

**Ready to start? Begin with Step 1 to clean up the current installation!**
