# Quick Installation Reference

## For Ubuntu Server 24.04 LTS Users

### Step 1: Fix Permissions (If Needed)
If you get "Permission denied" errors:
```bash
cd /app/scripts
sudo ./fix-permissions.sh
```

### Step 2: Run the Installer
```bash
cd /app/scripts
./install.sh
```

### Step 3: What Happens Next?

The installer will:

1. **Check for Python 3 and Node.js**
   - If missing, it will ask: "Would you like to install missing dependencies automatically?"
   - Press `Y` (or just Enter) to install them automatically
   - Press `N` to cancel and install manually

2. **Auto-Install Dependencies**
   - Installs Python 3.11+ with pip and venv
   - Installs Node.js 18.x from NodeSource repository
   - Verifies installation succeeded

3. **Choose Installation Method**
   - Option 1: Docker (containerized)
   - Option 2: Native (direct installation)
   - Option 3: SSL certificates
   - Option 4: Re-detect system
   - Option 5: Exit

### Supported Distributions

**Fully Supported (Auto-install works):**
- Ubuntu 20.04+
- Debian 10+
- CentOS 7+
- RHEL 7+

**Partial Support (Manual install needed):**
- Other Linux distributions - install Python 3 and Node.js manually first

## Manual Installation (Alternative)

If auto-install doesn't work for your distribution:

### Install Python 3
```bash
# Debian/Ubuntu
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv

# RHEL/CentOS
sudo yum install -y python3 python3-pip
```

### Install Node.js
```bash
# Using NodeSource (recommended)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Or from your distribution's repo
sudo apt-get install -y nodejs npm
```

### Run Installer
```bash
cd /app/scripts
./install.sh
```

## Troubleshooting

### "Permission denied" error
Run: `sudo /app/scripts/fix-permissions.sh`

### "Missing dependencies" error
The installer should offer to install them. If not, install manually (see above).

### "Command not found: node"
Make sure Node.js is in your PATH:
```bash
which node
node --version
```

If not found, reinstall Node.js using the commands above.

### Python version too old
The installer requires Python 3.11+. If your distribution's Python is older:
```bash
# Use deadsnakes PPA on Ubuntu
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv python3.11-dev
```

## Next Steps After Installation

### For Native Installation
```bash
# Start backend
cd /app/backend
source venv/bin/activate
python server.py

# Start frontend (in another terminal)
cd /app/frontend
yarn start
```

### For Docker Installation
```bash
cd /app
docker-compose up -d
```

### Access the Panel
- Frontend: http://localhost:3000
- Backend API: http://localhost:8001
- First-time setup will prompt for admin credentials

## Getting Help

- See `README.md` for complete documentation
- See `INSTALLATION_GUIDE.md` for installation method comparison
- See `INSTALLER_GUIDE.md` for detailed installer menu guide
- See `TROUBLESHOOTING.md` for common issues and solutions
