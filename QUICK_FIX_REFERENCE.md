# Quick Fix Reference Card

## Most Common Issues & Instant Solutions

### 1️⃣ WinSCP Permission Denied (Error Code 3)
```bash
# Always upload to /home/yourusername/ first, then:
sudo mv /home/yourusername/files /opt/destination/
```

### 2️⃣ Virtual Environment Creation Failed
```bash
sudo apt-get install -y python3-venv
```

### 3️⃣ MongoDB Repository Error (Ubuntu 24.04)
```bash
sudo rm -f /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt-get update
# Then re-run installer - it will handle MongoDB correctly
```

### 4️⃣ Node.js Version Too Old (Need 20.x)
```bash
sudo apt-get remove -y nodejs
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
node --version  # Verify it's 20.x
```

### 5️⃣ Frontend Dependencies Missing
```bash
cd /opt/Automated-Arma-Panel-main/frontend
yarn install
```

### 6️⃣ Services Failing - Wrong Paths
```bash
cd /opt/Automated-Arma-Panel-main/scripts
sudo bash ./setup-systemd.sh
```

---

## Quick Verification Commands

```bash
# Check what's installed
python3 --version
node --version
mongod --version
dpkg -l | grep python3-venv

# Check services
sudo systemctl status tactical-backend tactical-frontend

# Check if ports are listening
sudo ss -tuln | grep -E '3000|8001'

# View logs
sudo journalctl -u tactical-backend -n 20
sudo journalctl -u tactical-frontend -n 20
```

---

## Quick Access URLs

**From the VM itself:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8001/api/

**From your network:**
- Frontend: http://YOUR_VM_IP:3000
- Backend API: http://YOUR_VM_IP:8001/api/

---

## Emergency Commands

**Restart services:**
```bash
sudo systemctl restart tactical-backend tactical-frontend
```

**View real-time logs:**
```bash
sudo journalctl -u tactical-backend -f
```

**Stop everything:**
```bash
sudo systemctl stop tactical-backend tactical-frontend
```

**Fresh start:**
```bash
sudo systemctl stop tactical-backend tactical-frontend
sudo systemctl daemon-reload
sudo systemctl start tactical-backend tactical-frontend
```

---

## File Locations

| Component | Location |
|-----------|----------|
| Application | `/opt/Automated-Arma-Panel-main/` |
| Backend venv | `/opt/Automated-Arma-Panel-main/backend/venv/` |
| Frontend deps | `/opt/Automated-Arma-Panel-main/frontend/node_modules/` |
| Systemd services | `/etc/systemd/system/tactical-*.service` |
| Backend logs | `sudo journalctl -u tactical-backend` |
| Frontend logs | `sudo journalctl -u tactical-frontend` |
| MongoDB data | `/var/lib/mongodb/` |

---

## Installation Checklist

- [ ] python3-venv installed
- [ ] MongoDB running (`sudo systemctl status mongod`)
- [ ] Backend venv created (`ls /opt/.../backend/venv/`)
- [ ] Frontend deps installed (`ls /opt/.../frontend/node_modules/`)
- [ ] Services running (`systemctl status tactical-backend tactical-frontend`)
- [ ] Ports listening (`ss -tuln | grep -E '3000|8001'`)
- [ ] Can access frontend (http://VM_IP:3000)
- [ ] Firewall configured (`sudo ufw allow 3000/tcp 8001/tcp`)

---

## When All Else Fails

1. Collect logs:
   ```bash
   sudo journalctl -u tactical-backend -n 100 > backend.log
   sudo journalctl -u tactical-frontend -n 100 > frontend.log
   ```

2. Check systemd service files:
   ```bash
   cat /etc/systemd/system/tactical-backend.service
   cat /etc/systemd/system/tactical-frontend.service
   ```

3. Verify paths in service files match your installation directory

4. See detailed troubleshooting in:
   - `README.md` (Troubleshooting section)
   - `COMPLETE_VM_DEPLOYMENT_GUIDE.md`
   - `TROUBLESHOOTING_COMPLETE.md`
