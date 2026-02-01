# ⚠️ IMPORTANT: Installation Command

## TL;DR - How to Run the Installer

**Always use:**
```bash
cd /app/scripts
sudo bash ./install.sh
```

**DO NOT use:**
```bash
./install.sh  ❌ This will FAIL
```

---

## Why `sudo bash ./install.sh`?

### 1. Sudo Privileges Required
The installer needs root/sudo access to:
- Install system packages (Python, Node.js, MongoDB)
- Configure system services
- Create systemd service files
- Modify system-level configurations
- Set up firewall rules (if using SSL)

### 2. Bash Explicit Execution
Using `bash` explicitly ensures:
- Script runs even without execute permissions
- Consistent shell environment
- Bypasses any permission issues
- Works regardless of current user's shell

### 3. Common Mistakes

| Command | Result | Why? |
|---------|--------|------|
| `./install.sh` | ❌ FAILS | No execute permission or insufficient privileges |
| `sudo ./install.sh` | ⚠️ MAY FAIL | Depends on execute permission being set |
| `bash install.sh` | ❌ FAILS | No sudo - cannot install system packages |
| `sudo bash ./install.sh` | ✅ WORKS | Correct - has permissions and sudo |

---

## Complete Installation Flow

### Step 1: Navigate to Scripts Directory
```bash
cd /app/scripts
```

### Step 2: Run Installer with Sudo and Bash
```bash
sudo bash ./install.sh
```

### Step 3: Follow Interactive Menu
- Choose Option 2: Native Installation
- Installer will auto-detect missing Python/Node.js
- Approve automatic installation when prompted
- Complete guided configuration

### Step 4: Start Services
```bash
# Backend
cd /app/backend
source venv/bin/activate
python server.py

# Frontend (new terminal)
cd /app/frontend
yarn start
```

---

## If You Still Get Permission Errors

### Run the Permission Fix Script First:
```bash
cd /app/scripts
sudo bash ./fix-permissions.sh
```

Then retry the installer:
```bash
sudo bash ./install.sh
```

---

## Quick Reference

### Interactive Installation:
```bash
sudo bash ./install.sh
```

### Automatic Installation:
```bash
sudo bash ./install.sh --auto
```

### Help/Usage:
```bash
sudo bash ./install.sh --help
```

### Permission Fix:
```bash
sudo bash ./fix-permissions.sh
```

---

## What Gets Installed Automatically?

When you run the installer, it will:

1. **Check for Python 3**
   - If missing: Install Python 3.11+ with pip and venv
   
2. **Check for Node.js**
   - If missing: Install Node.js 18.x via NodeSource repository
   
3. **Check for MongoDB**
   - Prompt to install if missing
   
4. **Set Up Backend**
   - Create Python virtual environment
   - Install Python dependencies
   - Configure .env file
   
5. **Set Up Frontend**
   - Install Yarn if needed
   - Install Node.js dependencies
   - Configure .env file

6. **Create Directories**
   - /tmp/arma_servers
   - logs/
   - backups/

7. **Optional: Install SteamCMD**
   - Prompts user if they want to install
   - Downloads and extracts SteamCMD
   - Makes executable

---

## Platform-Specific Notes

### Ubuntu/Debian:
- Uses `apt-get` for package installation
- NodeSource deb repository for Node.js
- Full automation support

### RHEL/CentOS:
- Uses `yum` for package installation
- NodeSource rpm repository for Node.js
- Full automation support

### Other Linux Distributions:
- May require manual Python/Node.js installation
- Installer will notify if auto-install not supported
- Follow manual installation instructions in QUICK_INSTALL.md

---

## Remember

✅ **DO**: `sudo bash ./install.sh`

❌ **DON'T**: `./install.sh`

This simple change will save you from 99% of installation issues!
