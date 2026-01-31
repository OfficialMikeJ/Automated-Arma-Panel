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
- **Node.js**: 16.x or higher
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

### ⚠️ Ubuntu Server 24.04 LTS - Fix Permissions First

If you get "Permission denied" errors on Ubuntu Server, run this first:

```bash
cd /app/scripts
sudo ./fix-permissions.sh
```

This will fix ownership and make all scripts executable.

---

### Quick Start - Interactive Installer (Recommended)

The easiest way to install with guided setup:

```bash
cd /app/scripts
./install.sh
```

**Interactive Menu Features:**
- 🎯 Auto-detects existing installations
- 📋 5 easy options to choose from
- 🐳 Option 1: Install Docker & Docker Compose
- 💻 Option 2: Install Panel (Native) + Guided Setup
- 🔒 Option 3: Install SSL Certificates (Let's Encrypt)
- 🔄 Option 4: Restart/Re-detect System
- 🚪 Option 5: Exit with Quick Start Guide
- ✨ **NEW**: Auto-installs Python 3 & Node.js if missing

**See:** [INSTALLER_GUIDE.md](INSTALLER_GUIDE.md) for detailed menu documentation.

---

### Option 1: Automatic Installation

For experienced users who want one-command setup:

```bash
cd /app/scripts
./install.sh --auto
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

### Backend won't start
- Check if MongoDB is running: `sudo systemctl status mongod`
- Verify Python virtual environment is activated
- Check backend/.env configuration

### Frontend won't connect
- Verify REACT_APP_BACKEND_URL in frontend/.env
- Check if backend is running on correct port
- Clear browser cache and cookies

### Server processes won't start
- Check file permissions in /tmp/arma_servers/
- Verify port is not already in use
- Check server logs for errors

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
