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

- **OS**: Linux (Ubuntu 20.04+ recommended)
- **Python**: 3.11 or higher
- **Node.js**: 16.x or higher
- **Yarn**: 1.22.x or higher
- **MongoDB**: 4.4 or higher
- **RAM**: Minimum 2GB (4GB+ recommended)
- **Disk Space**: 5GB+ free space

## Installation

### Option 1: Automatic Installation (Recommended)

Run the automated installation script:

```bash
cd /app/scripts
chmod +x install.sh
./install.sh --auto
```

The script will:
- Install all required dependencies
- Set up Python virtual environment
- Install Node.js packages
- Configure MongoDB
- Create necessary directories
- Set up environment files

### Option 2: Manual Installation

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

### Production Mode

For production deployment, use the provided supervisor configuration or systemd services.

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
