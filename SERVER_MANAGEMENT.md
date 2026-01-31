# Server Management Implementation Guide

## Overview
This document describes the actual Arma Reforger dedicated server process management implementation in the Tactical Command panel.

## Changes Made

### Previous Implementation
- Used dummy bash loop processes that simulated server activity
- No actual Arma server executable integration
- Placeholder functionality only

### Current Implementation
- Real Arma Reforger server executable management
- Proper configuration file generation
- Process health monitoring
- Graceful shutdown with fallback to force kill
- Timestamped logging
- Enhanced error handling

## Server Management Features

### 1. Server Start (`POST /api/servers/{server_id}/start`)

**What it does:**
- Validates server isn't already running
- Creates necessary directory structure (logs, configs, profiles)
- Checks for server executable existence
- Generates `server.json` configuration if missing
- Starts Arma Reforger server with proper parameters
- Validates successful startup
- Returns PID and log file path

**Requirements:**
- Arma Reforger server files installed at `install_path`
- Executable: `ArmaReforgerServer` in the server directory
- Proper file permissions (executable bit set)

**Generated Configuration (`configs/server.json`):**
```json
{
  "bindAddress": "0.0.0.0",
  "bindPort": 2001,
  "publicAddress": "",
  "publicPort": 2001,
  "a2s": {
    "address": "",
    "port": 2017
  },
  "game": {
    "name": "Server Name",
    "password": "",
    "passwordAdmin": "changeme",
    "maxPlayers": 64,
    "visible": true
  },
  "mods": []
}
```

**Start Command:**
```bash
./ArmaReforgerServer \
  -config=configs/server.json \
  -profile=profiles \
  -maxFPS=60
```

**Response:**
```json
{
  "message": "Server started successfully",
  "status": "online",
  "pid": 12345,
  "log_file": "/path/to/server/logs/server_20250131_235959.log"
}
```

**Error Scenarios:**
- Server already running: Returns existing PID
- Executable not found: 400 error with installation instructions
- Startup failure: 500 error with log file reference

### 2. Server Stop (`POST /api/servers/{server_id}/stop`)

**What it does:**
- Sends SIGTERM for graceful shutdown
- Waits up to 10 seconds for process termination
- Falls back to SIGKILL if needed
- Updates database status
- Cleans up process group

**Graceful Shutdown Flow:**
1. Send SIGTERM to process group
2. Poll every second for 10 seconds
3. If still alive, send SIGKILL
4. Update database status to offline

**Response:**
```json
{
  "message": "Server stopped successfully",
  "status": "offline"
}
```

### 3. Server Restart (`POST /api/servers/{server_id}/restart`)

**What it does:**
- Sets status to "restarting"
- Performs graceful stop (same as stop endpoint)
- Waits 2 seconds for cleanup
- Starts server with same logic as start endpoint
- Updates status and PID

**Flow:**
1. Set status: "restarting"
2. Stop existing process (with graceful shutdown)
3. Wait 2 seconds
4. Validate executable and configuration
5. Start new process
6. Validate startup success
7. Update status to "online" or "offline"

**Response:**
```json
{
  "message": "Server restarted successfully",
  "status": "online",
  "pid": 12346,
  "log_file": "/path/to/server/logs/server_20250131_240102.log"
}
```

## Directory Structure

For each server instance:
```
{install_path}/
├── ArmaReforgerServer          # Server executable
├── configs/
│   └── server.json             # Generated/user configuration
├── profiles/                   # Server profiles and data
└── logs/
    ├── server_20250131_120000.log
    ├── server_20250131_130000.log
    └── server_20250131_140000.log
```

## Installing Arma Reforger Server

### Via SteamCMD:
```bash
# Navigate to installation directory
cd /path/to/server/install

# Install/update Arma Reforger server
~/steamcmd/steamcmd.sh \
  +login anonymous \
  +force_install_dir "$(pwd)" \
  +app_update 1874900 validate \
  +quit
```

**Steam App ID:** 1874900 (Arma Reforger Dedicated Server)

### Via Panel (Future Enhancement):
The panel can integrate SteamCMD to automatically download and install server files.

## Configuration Customization

Users can edit `configs/server.json` to customize:
- Server name and visibility
- Port numbers (game, A2S, RCON)
- Maximum players
- Admin password
- Game password
- Mods (Steam Workshop IDs)

## Firewall Configuration

Required ports for Arma Reforger:
- **Game Port:** 2001 (UDP/TCP) - Default, configurable
- **A2S Port:** Game Port + 16 (UDP) - Steam query
- **RCON Port:** Configurable in server.json

Example UFW rules:
```bash
sudo ufw allow 2001/tcp
sudo ufw allow 2001/udp
sudo ufw allow 2017/udp
```

## Logging

### Log File Naming:
`server_YYYYMMDD_HHMMSS.log`

### Log Location:
`{install_path}/logs/`

### Log Contents:
- Server startup messages
- Configuration loading
- Player connections
- Server events
- Error messages
- Shutdown messages

### Viewing Logs:
Available through the panel's log viewer modal or directly:
```bash
tail -f /path/to/server/logs/server_*.log
```

## Process Management

### Process Group:
- Uses `os.setsid()` to create new process group
- Ensures all child processes are killed together
- Prevents orphaned processes

### Signal Handling:
- **SIGTERM:** Graceful shutdown request
- **SIGKILL:** Force termination (last resort)
- **Process polling:** Used to check if process is alive

### Health Checks:
- Startup validation: Waits 2 seconds and checks if process still exists
- Status verification: Uses `os.kill(pid, 0)` to check process existence
- Database updates: Reflects actual process state

## Error Handling

### Common Errors:

**1. Executable Not Found:**
```
Server executable not found at /path/to/ArmaReforgerServer. 
Please install the server files first using SteamCMD (App ID: 1874900 for Arma Reforger).
```

**Solution:** Install server files via SteamCMD

**2. Startup Failure:**
```
Server failed to start. Check log file: /path/to/logs/server_*.log
```

**Solution:** 
- Check log file for specific error
- Verify port isn't in use
- Ensure proper file permissions
- Validate configuration file syntax

**3. Permission Denied:**
```
[Errno 13] Permission denied: '/path/to/ArmaReforgerServer'
```

**Solution:** 
```bash
chmod +x /path/to/ArmaReforgerServer
```

## Future Enhancements

### Planned Features:
1. **Auto-update:** Integrated SteamCMD updates via panel
2. **Mod management:** Workshop mod download and configuration
3. **RCON integration:** In-panel server commands
4. **Player management:** Kick, ban, whitelist
5. **Performance metrics:** Real-time CPU/RAM usage per server
6. **Scheduled restarts:** Automatic server restarts at specified times
7. **Backup/restore:** Server configuration and save backups

### Arma 4 Support:
- Currently prepared with `arma_4` game type
- Will be implemented when Arma 4 dedicated server is released
- Similar architecture and configuration expected

## Testing

### Manual Testing:
1. Create server instance in panel
2. Install Arma Reforger files via SteamCMD
3. Use panel to start server
4. Verify log file creation and server startup
5. Check process with `ps aux | grep ArmaReforgerServer`
6. Test stop and restart functionality

### Automated Testing:
Use the testing agent to validate:
- Server creation flow
- Start/stop/restart operations
- Error handling for missing files
- Configuration file generation
- Log file creation

## Support Resources

### Official Documentation:
- Bohemia Interactive Arma Reforger Wiki
- SteamCMD Documentation

### Community Resources:
- Arma Reforger Discord
- Bohemia Interactive Forums
- Reddit: r/arma

### Panel-Specific:
- Check `/app/TROUBLESHOOTING.md` for common issues
- View logs at `{install_path}/logs/`
- Contact support with log files if issues persist
