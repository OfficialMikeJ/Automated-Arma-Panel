# Panel Network Configuration

## Default Port Configuration

The Tactical Command panel is pre-configured to accept connections from any network interface:

### Backend API
- **Host:** `0.0.0.0` (All network interfaces)
- **Port:** `8001`
- **Access URLs:**
  - Local: `http://localhost:8001`
  - LAN: `http://YOUR_LOCAL_IP:8001`
  - WAN: `http://YOUR_PUBLIC_IP:8001` (with firewall configured)

### Frontend Panel
- **Host:** `0.0.0.0` (All network interfaces)
- **Port:** `3000`
- **Access URLs:**
  - Local: `http://localhost:3000`
  - LAN: `http://YOUR_LOCAL_IP:3000`
  - WAN: `http://YOUR_PUBLIC_IP:3000` (with firewall configured)

### MongoDB Database
- **Host:** `0.0.0.0` (All network interfaces - `--bind_ip_all`)
- **Port:** `27017`
- **⚠️ Security:** Only accessible internally via backend

---

## Supervisor Configuration

The panel services are managed by Supervisor with the following configuration:

**Backend (`/etc/supervisor/conf.d/supervisord.conf`):**
```ini
[program:backend]
command=/root/.venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001 --workers 1 --reload
directory=/app/backend
```

**Frontend (`/etc/supervisor/conf.d/supervisord.conf`):**
```ini
[program:frontend]
command=yarn start
environment=HOST="0.0.0.0",PORT="3000"
directory=/app/frontend
```

---

## Finding Your IP Addresses

### Local IP Address (LAN)
```bash
# Option 1: Using hostname
hostname -I | awk '{print $1}'

# Option 2: Using ip command
ip addr show | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | cut -d/ -f1

# Option 3: Using ifconfig
ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}'
```

### Public IP Address (WAN)
```bash
# Option 1: Using curl
curl -4 ifconfig.me

# Option 2: Using dig
dig +short myip.opendns.com @resolver1.opendns.com

# Option 3: Using wget
wget -qO- https://ipecho.net/plain
```

---

## Access Examples

### From Local Machine
```bash
# Backend API
curl http://localhost:8001/api/auth/check-first-run

# Frontend Panel
xdg-open http://localhost:3000  # Linux
open http://localhost:3000      # macOS
```

### From LAN (Other devices on same network)
Assuming your server's local IP is `192.168.1.100`:

```bash
# Backend API
curl http://192.168.1.100:8001/api/auth/check-first-run

# Frontend Panel (in browser)
http://192.168.1.100:3000
```

### From WAN (Internet)
Assuming your public IP is `203.0.113.50` and you've configured firewall and port forwarding:

```bash
# Frontend Panel (in browser)
http://203.0.113.50:3000

# Backend API
http://203.0.113.50:8001/api/
```

---

## Firewall Configuration

### Using UFW (Recommended)
The installer includes firewall configuration. Run:

```bash
cd /app/scripts
sudo bash ./install.sh
# Select Option 4: Configure Firewall (UFW)
```

This automatically opens:
- Port 22 (SSH)
- Port 3000 (Frontend)
- Port 8001 (Backend API)
- Ports 2001-2100 (Arma Servers)

### Manual UFW Configuration
```bash
# Allow panel ports
sudo ufw allow 3000/tcp comment 'Tactical Panel Frontend'
sudo ufw allow 8001/tcp comment 'Tactical Panel Backend'

# Allow Arma server ports
sudo ufw allow 2001:2100/tcp comment 'Arma Server Ports'
sudo ufw allow 2001:2100/udp comment 'Arma Server Ports'

# Enable firewall
sudo ufw enable
```

### Check Firewall Status
```bash
sudo ufw status verbose
```

---

## Port Forwarding (For WAN Access)

If you want to access the panel from the internet, configure port forwarding on your router:

### Router Configuration
Forward these ports from your router to your server's local IP:

| Service | Protocol | External Port | Internal IP | Internal Port |
|---------|----------|---------------|-------------|---------------|
| Frontend | TCP | 3000 | YOUR_SERVER_IP | 3000 |
| Backend | TCP | 8001 | YOUR_SERVER_IP | 8001 |
| SSH | TCP | 22 | YOUR_SERVER_IP | 22 |

**Example:**
- External Port: 3000 → Internal: 192.168.1.100:3000
- External Port: 8001 → Internal: 192.168.1.100:8001

---

## Changing Default Ports

### Backend Port (Change from 8001)

1. **Edit Supervisor Config:**
   ```bash
   sudo nano /etc/supervisor/conf.d/supervisord.conf
   ```
   
   Change:
   ```ini
   command=/root/.venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001
   ```
   
   To your desired port (e.g., 8080):
   ```ini
   command=/root/.venv/bin/uvicorn server:app --host 0.0.0.0 --port 8080
   ```

2. **Update Frontend .env:**
   ```bash
   nano /app/frontend/.env
   ```
   
   Change:
   ```
   REACT_APP_BACKEND_URL=https://yourdomain.com
   ```
   
   To use your new port.

3. **Update Firewall:**
   ```bash
   sudo ufw allow 8080/tcp comment 'Tactical Panel Backend'
   sudo ufw delete allow 8001/tcp
   ```

4. **Restart Services:**
   ```bash
   sudo supervisorctl restart backend frontend
   ```

### Frontend Port (Change from 3000)

1. **Edit Supervisor Config:**
   ```bash
   sudo nano /etc/supervisor/conf.d/supervisord.conf
   ```
   
   Change:
   ```ini
   environment=HOST="0.0.0.0",PORT="3000"
   ```
   
   To your desired port (e.g., 8080):
   ```ini
   environment=HOST="0.0.0.0",PORT="8080"
   ```

2. **Update Firewall:**
   ```bash
   sudo ufw allow 8080/tcp comment 'Tactical Panel Frontend'
   sudo ufw delete allow 3000/tcp
   ```

3. **Restart Services:**
   ```bash
   sudo supervisorctl restart frontend
   ```

---

## Security Best Practices

### 1. **Use SSL/HTTPS (Recommended for Production)**
```bash
cd /app/scripts
sudo bash ./install.sh
# Select Option 3: Install SSL Certificates
```

This sets up Let's Encrypt SSL and configures nginx as a reverse proxy.

### 2. **Restrict Access by IP (Optional)**

Allow only specific IPs:
```bash
# Allow specific IP to access frontend
sudo ufw delete allow 3000/tcp
sudo ufw allow from 203.0.113.10 to any port 3000 proto tcp comment 'Specific IP Only'

# Allow specific subnet
sudo ufw allow from 192.168.1.0/24 to any port 3000 proto tcp comment 'LAN Only'
```

### 3. **Change Default Ports**
Consider using non-standard ports to reduce automated scanning:
- Frontend: 3000 → 8443
- Backend: 8001 → 8444

### 4. **Use Strong Passwords**
The panel enforces password complexity by default:
- Minimum 8 characters
- Uppercase letter
- Lowercase letter
- Number
- Special character

### 5. **Enable TOTP/2FA**
Two-factor authentication is built-in. Enable it after first login.

---

## Troubleshooting

### Port Already in Use
```bash
# Check what's using port 3000
sudo lsof -i :3000

# Check what's using port 8001
sudo lsof -i :8001

# Kill process on port (if needed)
sudo kill -9 $(sudo lsof -t -i:3000)
```

### Cannot Access from LAN/WAN
```bash
# 1. Check firewall status
sudo ufw status

# 2. Check if services are running
sudo supervisorctl status

# 3. Check if services are listening on 0.0.0.0
sudo netstat -tlnp | grep -E ':3000|:8001'

# Should show:
# tcp  0  0 0.0.0.0:3000  0.0.0.0:*  LISTEN
# tcp  0  0 0.0.0.0:8001  0.0.0.0:*  LISTEN
```

### Test Connectivity
```bash
# From another machine, test if port is accessible
telnet YOUR_SERVER_IP 3000
# OR
nc -zv YOUR_SERVER_IP 3000

# Test backend API
curl http://YOUR_SERVER_IP:8001/api/auth/check-first-run
```

---

## Quick Reference

### Default Configuration
```
Backend:  0.0.0.0:8001
Frontend: 0.0.0.0:3000
MongoDB:  0.0.0.0:27017 (internal only)
```

### Service Management
```bash
# Status
sudo supervisorctl status

# Restart
sudo supervisorctl restart backend frontend

# Logs
sudo tail -f /var/log/supervisor/backend.out.log
sudo tail -f /var/log/supervisor/frontend.out.log
```

### Access URLs
```
Local:    http://localhost:3000
LAN:      http://YOUR_LOCAL_IP:3000
WAN:      http://YOUR_PUBLIC_IP:3000 (with firewall)
With SSL: https://yourdomain.com
```
