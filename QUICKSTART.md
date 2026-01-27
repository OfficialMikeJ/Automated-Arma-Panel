# Quick Start Guide

Get Tactical Command up and running in minutes!

## Prerequisites

- Linux server (Ubuntu 20.04+ recommended)
- sudo access
- Internet connection

## One-Command Installation

```bash
cd /app/scripts && chmod +x install.sh && ./install.sh --auto
```

This will automatically:
- Check system requirements
- Install missing dependencies (Yarn, MongoDB)
- Set up Python virtual environment
- Install all backend and frontend packages
- Configure environment files
- Create necessary directories

## Starting the Application

### 1. Start MongoDB (if not running)
```bash
sudo systemctl start mongod
sudo systemctl status mongod  # Verify it's running
```

### 2. Start Backend (Terminal 1)
```bash
cd /app/backend
source venv/bin/activate
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### 3. Start Frontend (Terminal 2)
```bash
cd /app/frontend
yarn start
```

### 4. Access the Panel
Open your browser and navigate to:
```
http://localhost:3000
```

## First Login

1. Click **Register** to create your admin account
2. Enter a username and password
3. Click **Register** again
4. You'll be automatically logged in to the dashboard

## Quick Setup

### Install SteamCMD
1. Click **SteamCMD Manager** button
2. Click **Install SteamCMD**
3. Wait for installation (takes ~30 seconds)

### Add Your First Server
1. Click **Add Server Instance**
2. Fill in the details:
   - **Server Name**: My First Server
   - **Game Type**: Arma Reforger
   - **Port**: 2302
   - **Max Players**: 64
   - **Install Path**: /home/steamcmd/servers/server1
3. Click **Add Server**

### Start Your Server
1. Find your server card in the dashboard
2. Click the **Start** button (green play icon)
3. Watch the status indicator turn green (Online)

### Configure Your Server
1. Click **Config** button on the server card
2. Edit the configuration file as needed
3. Click **Save Config**

### Add Mods
1. Click **Mods** button on the server card
2. Click **Add Mod**
3. Enter Workshop ID and Mod Name
4. Click **Add Mod**
5. Use the toggle to enable/disable mods

### View Logs
1. Click **Logs** button on the server card
2. Enable **Auto Refresh** for real-time monitoring
3. Use the refresh button to manually update

## Troubleshooting

### Port Already in Use
If you see "port already in use" errors:
```bash
# Check what's using the port
sudo lsof -i :8001  # for backend
sudo lsof -i :3000  # for frontend

# Kill the process if needed
sudo kill -9 <PID>
```

### MongoDB Not Starting
```bash
# Check MongoDB status
sudo systemctl status mongod

# View logs
sudo journalctl -u mongod -n 50

# Restart MongoDB
sudo systemctl restart mongod
```

### Backend Connection Errors
Check your `.env` files:

**Backend** (`/app/backend/.env`):
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=arma_server_panel
SECRET_KEY=<your-generated-key>
CORS_ORIGINS=*
```

**Frontend** (`/app/frontend/.env`):
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

### Python Virtual Environment Issues
```bash
cd /app/backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Node Modules Issues
```bash
cd /app/frontend
rm -rf node_modules yarn.lock
yarn install
```

## Production Deployment

For production deployment, see the full [README.md](README.md) for:
- HTTPS setup with SSL certificates
- Supervisor/systemd service configuration
- Firewall rules
- Security hardening
- Performance optimization

## Need Help?

- Read the full [README.md](README.md) for detailed documentation
- Check the [API Endpoints](README.md#api-endpoints) section
- Review the [Troubleshooting](README.md#troubleshooting) guide
- Open an issue on GitHub

## Default Ports

- **Backend**: 8001
- **Frontend**: 3000
- **MongoDB**: 27017
- **Arma Servers**: 2302+ (configurable)

## Next Steps

1. Explore all dashboard features
2. Configure your server settings
3. Add mods from Steam Workshop
4. Monitor system resources
5. Check server logs regularly
6. Create backups of your configuration

---

**Enjoy managing your Arma servers with Tactical Command! 🎮**
