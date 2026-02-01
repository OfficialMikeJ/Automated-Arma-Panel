# Tactical Command - Arma Server Management Panel

A lightweight, fast, and responsive server management panel for Arma Reforger and Arma 4 game servers on Linux. Built with a tactical military-inspired UI theme.

![Tactical Command Dashboard](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![License](https://img.shields.io/badge/License-MIT-blue)

## Features

### Core Functionality
- **JWT Authentication** - Secure user registration and login system
- **Server Instance Management** - Create, configure, and manage multiple Arma server instances
- **Real-time Process Control** - Start, stop, and restart servers with actual process management
- **System Resource Monitoring** - Live CPU, Memory, and Disk usage with animated pie charts
- **SteamCMD Integration** - One-click SteamCMD installation for server deployment

### Advanced Features
- **Configuration Editor** - Full-featured editor for server.cfg files with syntax highlighting
- **Mod Management** - Add, enable/disable, and remove mods via Workshop IDs
- **Real-time Log Viewer** - View server logs with auto-refresh capability
- **Multiple Server Support** - Manage unlimited Arma Reforger and Arma 4 instances
- **Tactical UI Theme** - Military-grade design with glassmorphism and custom styling

## Technology Stack

### Backend
- **FastAPI** - High-performance Python web framework
- **MongoDB** - NoSQL database for flexible data storage
- **Motor** - Async MongoDB driver
- **psutil** - System and process utilities
- **JWT** - Secure token-based authentication
- **bcrypt** - Password hashing

### Frontend
- **React 19** - Modern UI library
- **Tailwind CSS** - Utility-first CSS framework
- **Recharts** - Composable charting library
- **Axios** - HTTP client
- **Lucide React** - Icon library
- **Sonner** - Toast notifications

## System Requirements

### For Native Installation
- **OS**: Linux (Ubuntu 20.04+ recommended)
- **Python**: 3.11 or higher
- **Node.js**: 20.x or higher (required for React Router 7+)
- **Yarn**: 1.22.x or higher
- **MongoDB**: 4.4 or higher
- **RAM**: Minimum 2GB (4GB+ recommended)
- **Disk Space**: 5GB+ free space

### For Docker Installation
- **OS**: Any Linux with Docker support
- **Docker**: 20.10 or higher
- **Docker Compose**: 2.0 or higher
- **RAM**: Minimum 4GB (for containers)
- **Disk Space**: 3GB+ free space

## Choosing Your Installation Method

### 🐳 Choose Docker If:
- You want **quick deployment** (2-3 minutes)
- You're deploying to **production**
- You need **environment isolation**
- You want **easy cleanup/removal**
- You're deploying to **multiple servers**

### 💻 Choose Native If:
- You're **developing/testing** locally
- You want **direct file access**
- You prefer **traditional setup**
- You have **resource constraints**
- You want **system integration** (systemd)

**Need help deciding?** See [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) for detailed comparison.

## Installation

### 🛠️ Automated Diagnostic & Repair Tool (NEW!)

If you encounter any installation issues, use our automated diagnostic tool:

```bash
cd /app/scripts
sudo bash ./diagnose-and-fix.sh
```

This tool will:
- Check all installation requirements
- Identify missing or corrupted components  
- Offer to fix issues automatically with yes/no prompts
- Verify the installation is complete and healthy

**Run this tool:**
- After installation if something doesn't work
- Before reporting issues
- Anytime you want to verify the installation

---

### ⚠️ Ubuntu Server 24.04 LTS - Important Installation Note

**Always use `sudo bash` to run the installer:**

```bash
cd /app/scripts
sudo bash ./install.sh
```

**Why?** The installer needs sudo privileges to install dependencies and configure the system. Using `./install.sh` alone may result in "Permission denied" errors.

If you still encounter permission issues, run the fix script first:

```bash
cd /app/scripts
sudo bash ./fix-permissions.sh
```

---

### Quick Start - Interactive Installer (Recommended)

The easiest way to install with guided setup:

```bash
cd /app/scripts
sudo bash ./install.sh
```

**What happens:** The installer will auto-detect if Python 3 or Node.js are missing and offer to install them for you!

**Interactive Menu Features:**
- 🎯 Auto-detects existing installations
- 📋 5 easy options to choose from
- 🐳 Option 1: Install Docker & Docker Compose
- 💻 Option 2: Install Panel (Native) + Guided Setup
- 🔒 Option 3: Install SSL Certificates (Let's Encrypt)
- 🔄 Option 4: Restart/Re-detect System
- 🚪 Option 5: Exit with Quick Start Guide
- ✨ **NEW**: Auto-installs Python 3 & Node.js if missing

**Need help?** See [QUICK_INSTALL.md](QUICK_INSTALL.md) for step-by-step instructions.

**See:** [INSTALLER_GUIDE.md](INSTALLER_GUIDE.md) for detailed menu documentation.

---

### Option 1: Automatic Installation

For experienced users who want one-command setup:

```bash
cd /app/scripts
sudo bash ./install.sh --auto
```

The script will:
- Install all required dependencies
- Set up Python virtual environment
- Install Node.js packages
- Configure MongoDB
- Create necessary directories
- Set up environment files

---

### Option 2: Docker Installation (Alternative)

If you prefer containerized deployment with Docker:

**Prerequisites:**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

**Deploy with Docker:**
```bash
cd /app

# Configure environment (optional)
# Edit docker-compose.yml if needed

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Access the panel
# Frontend: http://localhost:3000
# Backend: http://localhost:8001
```

**Docker Benefits:**
- Isolated environment
- No dependency conflicts
- Easy cleanup and removal
- Consistent across systems
- Production-ready configuration

**Docker Services:**
- MongoDB with persistent storage
- Backend API with health checks
- Frontend with optimized nginx build

**Note:** Docker is completely optional. The interactive installer (Option 1) lets you choose between Docker or Native installation.

### Option 3: Manual Installation (Advanced)

**Note:** You can skip this if using Option 1 (automatic) or Option 2 (Docker).

#### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd tactical-command-panel
```

#### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
yarn install
```

#### 4. MongoDB Setup

```bash
# Install MongoDB (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y mongodb-org

# Start MongoDB service
sudo systemctl start mongod
sudo systemctl enable mongod
```

#### 5. Environment Configuration

**Backend** (`/app/backend/.env`):
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=arma_server_panel
CORS_ORIGINS=*
SECRET_KEY=your-secret-key-here-change-in-production
```

**Frontend** (`/app/frontend/.env`):
```env
REACT_APP_BACKEND_URL=http://localhost:8001
WDS_SOCKET_PORT=0
ENABLE_HEALTH_CHECK=false
```

## Dependencies

### Backend Dependencies (requirements.txt)
```
fastapi==0.110.1
uvicorn==0.25.0
motor==3.3.1
pymongo==4.5.0
pydantic>=2.6.4
python-dotenv>=1.0.1
PyJWT>=2.10.1
passlib>=1.7.4
bcrypt==4.1.3
psutil>=7.2.0
python-multipart>=0.0.9
requests>=2.31.0
```

### Frontend Dependencies (package.json)
```json
{
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "react-router-dom": "^7.5.1",
    "axios": "^1.8.4",
    "recharts": "^3.6.0",
    "lucide-react": "^0.507.0",
    "sonner": "^2.0.3",
    "tailwindcss": "^3.4.17",
    "@radix-ui/react-*": "latest"
  }
}
```

## Running the Application

### Development Mode

**Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

**Frontend:**
```bash
cd frontend
yarn start
```

Access the application at `http://localhost:3000`

## Deployment Options

### Option 1: Docker Compose (Recommended for Production)

The easiest way to deploy in production with full isolation and easy management.

**Quick Start:**
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build
```

**Services Included:**
- MongoDB (persistent data with volumes)
- Backend API (auto-restart, health checks)
- Frontend (nginx, optimized build)

**Configuration:**
Edit `docker-compose.yml` to customize:
- Ports
- Environment variables
- Volume mounts
- Resource limits

**Access:**
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8001`
- MongoDB: `localhost:27017`

**Docker Architecture:**
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│    Backend      │────▶│    MongoDB      │
│  (nginx:80)     │     │  (uvicorn:8001) │     │  (mongo:27017)  │
│  React Build    │     │   FastAPI       │     │   Database      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

**Volume Management:**
```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect tactical-command-panel_mongodb_data

# Backup volume
docker run --rm -v tactical-command-panel_mongodb_data:/data -v $(pwd):/backup ubuntu tar czf /backup/mongodb-backup.tar.gz /data

# Remove volumes (⚠️ deletes all data!)
docker-compose down -v
```

**Troubleshooting Docker:**
```bash
# View container logs
docker logs tactical-backend
docker logs tactical-frontend
docker logs tactical-mongodb

# Enter container shell
docker exec -it tactical-backend bash
docker exec -it tactical-mongodb mongosh

# Check container health
docker ps
docker inspect tactical-backend

# Rebuild specific service
docker-compose up -d --build backend
```

### Option 2: Systemd Services (Linux Production)

For native Linux deployment with automatic startup on boot.

**Setup:**
```bash
# Run as root
cd /app/scripts
sudo ./setup-systemd.sh
```

This will:
- Create www-data user
- Set proper permissions
- Install systemd services
- Enable auto-start on boot
- Start services immediately

**Service Management:**
```bash
# Status
sudo systemctl status tactical-backend
sudo systemctl status tactical-frontend

# Start/Stop
sudo systemctl start tactical-backend
sudo systemctl stop tactical-frontend

# Restart
sudo systemctl restart tactical-backend

# View logs
sudo journalctl -u tactical-backend -f
sudo journalctl -u tactical-frontend -f

# Disable auto-start
sudo systemctl disable tactical-backend
```

**Service Files:**
- Backend: `/etc/systemd/system/tactical-backend.service`
- Frontend: `/etc/systemd/system/tactical-frontend.service`

### Option 3: Manual Supervisor (Current Setup)

If already using supervisor:

```bash
sudo supervisorctl restart backend frontend
sudo supervisorctl status
```

## Backup and Restore

### Creating Backups

**Automatic backup with timestamp:**
```bash
cd /app/scripts
./backup.sh
```

**Named backup:**
```bash
./backup.sh my-important-backup
```

**What's backed up:**
- MongoDB database (all collections)
- Server configurations
- Server logs (last 7 days)
- Environment files (.env)

**Backup location:** `/app/backups/`

**Automatic cleanup:** Keeps last 10 backups

### Restoring Backups

**List available backups:**
```bash
cd /app/scripts
./restore.sh
```

**Restore specific backup:**
```bash
./restore.sh backup_20240127_153045
```

**What happens during restore:**
1. Services are stopped
2. Database is dropped and restored
3. Configurations are restored
4. Logs are restored
5. Environment files are restored
6. Services are restarted

**⚠️ Warning:** Restore will overwrite existing data!

### Scheduled Backups

**Create daily backup with cron:**
```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /app/scripts/backup.sh >> /app/logs/backup.log 2>&1
```

**Weekly backup:**
```bash
0 2 * * 0 /app/scripts/backup.sh weekly-backup >> /app/logs/backup.log 2>&1
```

## Accessing the Panel

### Default Network Configuration
The panel is configured to accept connections from any network interface:

- **Frontend:** `0.0.0.0:3000` (accessible from any IP)
- **Backend API:** `0.0.0.0:8001` (accessible from any IP)

### Access URLs

**Local Access:**
```
Frontend: http://localhost:3000
Backend:  http://localhost:8001
```

**LAN Access (from other devices on your network):**
```
Frontend: http://YOUR_SERVER_IP:3000
Backend:  http://YOUR_SERVER_IP:8001
```

**WAN Access (from internet - requires firewall configuration):**
```
Frontend: http://YOUR_PUBLIC_IP:3000
Backend:  http://YOUR_PUBLIC_IP:8001
```

**📘 Full guide:** See [NETWORK_CONFIGURATION.md](NETWORK_CONFIGURATION.md) for:
- Finding your IP addresses
- Firewall configuration
- Port forwarding setup
- SSL/HTTPS configuration
- Changing default ports
- Security best practices

---

## Quick Start After Installation

## Usage Guide

### 1. First Time Setup

1. Navigate to the application URL
2. Click "Register" and create your admin account
3. Log in with your credentials

### 2. Installing SteamCMD

1. Click "SteamCMD Manager" button
2. Click "Install SteamCMD"
3. Wait for installation to complete

### 3. Adding a Server Instance

1. Click "Add Server Instance"
2. Fill in server details:
   - Server Name
   - Game Type (Arma Reforger or Arma 4)
   - Port Number
   - Max Players
   - Install Path
3. Click "Add Server"

### 4. Managing Servers

**Start/Stop/Restart:**
- Use the control buttons on each server card
- Green indicator = Online
- Gray indicator = Offline
- Amber indicator = Restarting

**Configuration:**
- Click "Config" button to edit server.cfg
- Modify settings as needed
- Click "Save Config"

**Mods:**
- Click "Mods" button
- Click "Add Mod"
- Enter Workshop ID and Mod Name
- Toggle mods on/off using the switch icon

**Logs:**
- Click "Logs" button to view server logs
- Enable "Auto Refresh" for real-time monitoring
- Logs update every 3 seconds when enabled

## Project Structure

```
/app/
├── backend/
│   ├── server.py              # Main FastAPI application
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Backend environment variables
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── ServerCard.js
│   │   │   ├── SystemResources.js
│   │   │   ├── ConfigEditorModal.js
│   │   │   ├── ModManagerModal.js
│   │   │   └── LogViewerModal.js
│   │   ├── pages/            # Page components
│   │   │   ├── LoginPage.js
│   │   │   └── DashboardPage.js
│   │   ├── App.js            # Main App component
│   │   └── index.css         # Global styles
│   ├── package.json          # Node dependencies
│   ├── tailwind.config.js    # Tailwind configuration
│   └── .env                  # Frontend environment variables
├── scripts/
│   └── install.sh            # Installation script
└── README.md                 # This file
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user

### Server Management
- `GET /api/servers` - List all servers
- `POST /api/servers` - Create new server
- `GET /api/servers/{id}` - Get server details
- `PATCH /api/servers/{id}` - Update server
- `DELETE /api/servers/{id}` - Delete server
- `POST /api/servers/{id}/start` - Start server
- `POST /api/servers/{id}/stop` - Stop server
- `POST /api/servers/{id}/restart` - Restart server

### Configuration
- `GET /api/servers/{id}/config` - Get server config
- `PUT /api/servers/{id}/config` - Update server config

### Mods
- `GET /api/servers/{id}/mods` - List server mods
- `POST /api/servers/{id}/mods` - Add mod
- `DELETE /api/servers/{id}/mods/{mod_id}` - Delete mod
- `PATCH /api/servers/{id}/mods/{mod_id}/toggle` - Toggle mod

### Logs & Resources
- `GET /api/servers/{id}/logs` - Get server logs
- `GET /api/system/resources` - Get system resources
- `GET /api/steamcmd/status` - Get SteamCMD status
- `POST /api/steamcmd/install` - Install SteamCMD

## Security Notes

1. **Change Default Secret Key**: Update `SECRET_KEY` in backend/.env
2. **Use HTTPS**: In production, always use HTTPS with valid SSL certificates
3. **Firewall Configuration**: Only expose necessary ports
4. **MongoDB Security**: Configure MongoDB authentication in production
5. **Regular Updates**: Keep all dependencies up to date

## Troubleshooting

### Common Installation Issues

#### 1. WinSCP Permission Denied (Error Code 3)

**Problem:** Cannot upload/overwrite files in `/opt/` directory

**Solution:**
```bash
# Upload files to your home directory first
# In WinSCP: drag files to /home/yourusername/

# Then in SSH terminal:
cd /home/yourusername
sudo mv your-files /opt/Automated-Arma-Panel-main/
sudo chown -R root:root /opt/Automated-Arma-Panel-main/
```

**Or temporarily change ownership for WinSCP:**
```bash
sudo chown -R yourusername:yourusername /opt/Automated-Arma-Panel-main
# Upload files via WinSCP
sudo chown -R root:root /opt/Automated-Arma-Panel-main
```

---

#### 2. Python Virtual Environment Creation Failed

**Problem:** Installation fails with `venv/bin/activate: No such file or directory`

**Cause:** Missing `python3-venv` package

**Solution:**
```bash
# Install the required package
sudo apt-get update
sudo apt-get install -y python3-venv

# Verify installation
dpkg -l | grep python3-venv

# Re-run the installer
cd /opt/Automated-Arma-Panel-main/scripts
sudo bash ./install.sh
```

---

#### 3. MongoDB Repository Error (Ubuntu 24.04)

**Problem:** MongoDB installation fails with repository Release file error

**Cause:** MongoDB 7.0 repository doesn't have Ubuntu 24.04 (Noble) support yet

**Solution:**
```bash
# Remove problematic repository
sudo rm -f /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt-get update

# Install using modern method
sudo apt-get install -y gnupg curl
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
    sudo gpg --dearmor -o /usr/share/keyrings/mongodb-server-7.0.gpg

# For Ubuntu 24.04, use jammy repository
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | \
    sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

sudo apt-get update
sudo apt-get install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod
```

**Or use the updated installer which includes this fix automatically.**

---

#### 4. Node.js Version Too Old

**Problem:** Frontend installation fails with `The engine "node" is incompatible with this module. Expected version ">=20.0.0"`

**Cause:** React Router 7+ requires Node.js 20.x or higher

**Solution:**
```bash
# Remove old Node.js
sudo apt-get remove -y nodejs

# Add NodeSource repository for Node.js 20.x
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -

# Install Node.js 20.x
sudo apt-get install -y nodejs

# Verify version (should be v20.x.x)
node --version

# Install frontend dependencies
cd /opt/Automated-Arma-Panel-main/frontend
yarn install
```

**Note:** Updated installer automatically installs Node.js 20.x for new installations.

---

#### 5. Frontend node_modules Missing

**Problem:** Frontend service fails with `CHDIR` error or `node_modules` not found

**Solution:**
```bash
# Manually install frontend dependencies
cd /opt/Automated-Arma-Panel-main/frontend
yarn install

# If yarn is not installed:
npm install -g yarn
yarn install
```

---

#### 6. Systemd Services Failing - Wrong Paths

**Problem:** Services show `activating (auto-restart)` or fail with path errors

**Cause:** Service files have hardcoded `/app/` paths from development environment

**Solution Method 1 - Use setup script:**
```bash
cd /opt/Automated-Arma-Panel-main/scripts
sudo bash ./setup-systemd.sh
```

**Solution Method 2 - Manual fix:**
```bash
# Stop failing services
sudo systemctl stop tactical-backend
sudo systemctl stop tactical-frontend

# Remove old service files
sudo rm /etc/systemd/system/tactical-backend.service
sudo rm /etc/systemd/system/tactical-frontend.service

# Create backend service with correct paths
sudo tee /etc/systemd/system/tactical-backend.service > /dev/null << 'EOF'
[Unit]
Description=Tactical Command Backend Service
After=network.target mongodb.service
Wants=mongodb.service

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/opt/Automated-Arma-Panel-main/backend

ExecStart=/opt/Automated-Arma-Panel-main/backend/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001 --workers 1

Restart=always
RestartSec=10

StandardOutput=journal
StandardError=journal
SyslogIdentifier=tactical-backend

LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
EOF

# Create frontend service with correct paths
sudo tee /etc/systemd/system/tactical-frontend.service > /dev/null << 'EOF'
[Unit]
Description=Tactical Command Frontend Service
After=network.target tactical-backend.service
Wants=tactical-backend.service

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/opt/Automated-Arma-Panel-main/frontend

Environment="HOST=0.0.0.0"
Environment="PORT=3000"

ExecStart=/usr/bin/yarn start

Restart=always
RestartSec=10

StandardOutput=journal
StandardError=journal
SyslogIdentifier=tactical-frontend

LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
EOF

# Reload and start services
sudo systemctl daemon-reload
sudo systemctl enable tactical-backend
sudo systemctl enable tactical-frontend
sudo systemctl start tactical-backend
sudo systemctl start tactical-frontend

# Verify services are running
sudo systemctl status tactical-backend
sudo systemctl status tactical-frontend
```

---

#### 7. "Panel not fully installed" Warning

**Problem:** Installation shows `[WARNING] ✗ Panel not fully installed` at the beginning

**This is NORMAL!** This warning appears at the START of installation as a status check. The installer checks if backend/venv and frontend/node_modules exist before installation begins.

**What to check:**
- Did the installation complete successfully at the END?
- Do these directories exist after installation?
  ```bash
  ls -la /opt/Automated-Arma-Panel-main/backend/venv/
  ls -la /opt/Automated-Arma-Panel-main/frontend/node_modules/ | head
  ```
- Are services running?
  ```bash
  sudo systemctl status tactical-backend
  sudo systemctl status tactical-frontend
  ```

If installation completed but services still fail, see issue #6 above.

---

### Service Issues

#### Backend won't start
```bash
# Check MongoDB is running
sudo systemctl status mongod

# Check backend logs
sudo journalctl -u tactical-backend -n 50 --no-pager

# Verify environment variables
cat /opt/Automated-Arma-Panel-main/backend/.env

# Test manually
cd /opt/Automated-Arma-Panel-main/backend
source venv/bin/activate
uvicorn server:app --host 0.0.0.0 --port 8001
```

#### Frontend won't connect
```bash
# Check frontend logs
sudo journalctl -u tactical-frontend -n 50 --no-pager

# Verify backend URL
cat /opt/Automated-Arma-Panel-main/frontend/.env

# Check if ports are listening
sudo ss -tuln | grep -E '3000|8001'

# Test manually
cd /opt/Automated-Arma-Panel-main/frontend
yarn start
```

#### Cannot Access Panel from Browser

**Problem:** Cannot access http://192.168.2.26:3000 from your network

**Solution:**
```bash
# Check if services are running
sudo systemctl status tactical-backend
sudo systemctl status tactical-frontend

# Check if firewall is blocking
sudo ufw status

# Allow ports if needed
sudo ufw allow 3000/tcp
sudo ufw allow 8001/tcp

# Test locally first
curl http://localhost:3000
curl http://localhost:8001/api/auth/check-first-run

# If local works but remote doesn't, check network/router
```

#### Server processes won't start
- Check file permissions in /tmp/arma_servers/
- Verify port is not already in use
- Check server logs for errors
- Ensure Arma server files are installed

---

### Complete Fresh Reinstall

If all else fails, start fresh:

```bash
# Stop services
sudo systemctl stop tactical-backend
sudo systemctl stop tactical-frontend
sudo systemctl disable tactical-backend
sudo systemctl disable tactical-frontend

# Remove service files
sudo rm /etc/systemd/system/tactical-backend.service
sudo rm /etc/systemd/system/tactical-frontend.service
sudo systemctl daemon-reload

# Remove installation directory
sudo rm -rf /opt/Automated-Arma-Panel-main

# Re-download/copy files
# ... copy files to /opt/Automated-Arma-Panel-main ...

# Run installer
cd /opt/Automated-Arma-Panel-main/scripts
sudo bash ./install.sh
```

---

### Getting Help

**Before asking for help, collect this information:**

```bash
# System info
uname -a
lsb_release -a

# Check installations
python3 --version
node --version
mongod --version
dpkg -l | grep python3-venv

# Check services
sudo systemctl status tactical-backend
sudo systemctl status tactical-frontend

# Check logs
sudo journalctl -u tactical-backend -n 100 --no-pager
sudo journalctl -u tactical-frontend -n 100 --no-pager

# Check directories
ls -la /opt/Automated-Arma-Panel-main/backend/venv/
ls -la /opt/Automated-Arma-Panel-main/frontend/node_modules/ | head
```

**Useful Documentation:**
- `COMPLETE_VM_DEPLOYMENT_GUIDE.md` - Comprehensive deployment guide
- `INSTALLATION_GUIDE.md` - Detailed installation instructions
- `TROUBLESHOOTING_COMPLETE.md` - Extended troubleshooting
- `INSTALLATION_FIXES.md` - Recent bug fixes and solutions

## Performance Optimization

- **System Resources**: Auto-refreshes every 5 seconds
- **Log Viewer**: Limited to last 100 lines by default
- **Process Management**: Uses process groups for efficient cleanup
- **Database**: Indexes on user_id and server_id for fast queries

## Contributing

Contributions are welcome! Please follow these guidelines:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - feel free to use this project for personal or commercial purposes.

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

## Roadmap

- [ ] Server backup/restore functionality
- [ ] Scheduled restarts with cron-like scheduling
- [ ] Discord webhook notifications
- [ ] Server template system
- [ ] Multi-user role management
- [ ] Server performance metrics history
- [ ] Automated mod updates
- [ ] Server migration tools

## Credits

Built with ❤️ using modern web technologies.

- **Design**: Tactical Command theme inspired by military HUD interfaces
- **Icons**: Lucide React
- **Fonts**: Google Fonts (Inter, Barlow Condensed, JetBrains Mono)
- **Images**: Unsplash (tactical/military themed)
