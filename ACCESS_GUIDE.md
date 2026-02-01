# How to Access Your Tactical Panel - CRITICAL INFORMATION

## 🚨 IMPORTANT: Where Is Your Panel Actually Running?

### Current Situation

**Your panel is running on the EMERGENT CLOUD SERVER:**
- IP Address: 10.208.144.125
- Location: Emergent cloud infrastructure
- Access: Via Emergent's provided URL

**Your local VM (192.168.2.26):**
- Status: Application NOT installed yet
- Location: Your local network
- Access: Not available yet (needs deployment)

---

## ✅ HOW TO ACCESS NOW (Emergent Cloud)

### Option 1: Use Emergent's Preview URL (Recommended)

The panel is accessible through Emergent's preview system:

**Check your Emergent dashboard for the preview URL, it will look like:**
```
https://reforgerctl.preview.emergentagent.com
```

### Option 2: Direct IP Access (If Allowed)

Try accessing via the cloud server's IP:
```
http://10.208.144.125:3000
```

**Note:** This may not work due to Emergent's network configuration/firewall.

---

## ❌ WHY 192.168.2.26:3000 DOESN'T WORK

You're trying to access: `http://192.168.2.26:3000`

**Problem:** Nothing is running on 192.168.2.26 yet!

```
┌─────────────────────────────────┐
│  Emergent Cloud (10.208.144.125)│
│  ✅ Panel IS running here       │
│  ✅ Services: RUNNING            │
│  ✅ Port 3000: LISTENING         │
└─────────────────────────────────┘
              ║
              ║ You need to deploy from here
              ║
              ▼
┌─────────────────────────────────┐
│  Your Local VM (192.168.2.26)  │
│  ❌ Panel NOT running here      │
│  ❌ Services: NOT INSTALLED     │
│  ❌ Port 3000: NOTHING          │
└─────────────────────────────────┘
              ▲
              ║
              ║ You're trying to access here
              ║
      [Your Desktop/Browser]
```

---

## 🎯 TWO SOLUTIONS

### Solution A: Access Emergent Cloud Panel (Quick)

**Use Emergent's preview URL:**

1. Log into Emergent dashboard
2. Find your project/agent
3. Look for "Preview" or "Live URL"
4. Click the preview link

**OR ask Emergent support for your preview URL**

### Solution B: Deploy to Your Local VM (Recommended for Production)

This requires deploying the application TO your VM at 192.168.2.26.

**Steps:**

**1. Package the Application (on Emergent cloud)**
```bash
cd /app
tar -czf tactical-panel.tar.gz \
  --exclude=node_modules \
  --exclude=backend/venv \
  --exclude=backend/__pycache__ \
  --exclude=.git \
  backend/ frontend/ scripts/ *.md
```

**2. Download to Your Computer**

From your desktop:
```bash
# Get the file from Emergent cloud
scp root@10.208.144.125:/app/tactical-panel.tar.gz ~/Downloads/
```

**3. Upload to Your VM**
```bash
# Upload to your local VM
scp ~/Downloads/tactical-panel.tar.gz mike@192.168.2.26:/home/mike/
```

**4. Install on Your VM**

SSH into your VM:
```bash
ssh mike@192.168.2.26

# Extract and install
sudo mkdir -p /app
cd /home/mike
sudo tar -xzf tactical-panel.tar.gz -C /app

# Run installer
cd /app/scripts
sudo bash ./install.sh
# Select Option 2: Native Installation
```

**5. Access on Your VM**

After installation completes:
```
http://192.168.2.26:3000
```

---

## 🔍 VERIFICATION COMMANDS

### On Emergent Cloud (10.208.144.125)

Check if services are running:
```bash
sudo supervisorctl status
curl http://localhost:3000
```

Should see: Services RUNNING and HTML response

### On Your Local VM (192.168.2.26)

Check if services are running:
```bash
sudo systemctl status tactical-backend tactical-frontend
curl http://localhost:3000
```

Should see: Services RUNNING (after deployment)

---

## 🌐 NETWORK DIAGRAM

```
[Internet]
    │
    ├─── Emergent Cloud (10.208.144.125)
    │    └─── ✅ Panel Running Here
    │         └─── Preview URL: https://reforgerctl.preview.emergentagent.com
    │
    └─── Your Home Network
         │
         ├─── Your Router/Modem
         │    └─── 192.168.2.1 (gateway)
         │
         ├─── Your Desktop
         │    └─── 192.168.2.x
         │
         └─── Your VM
              └─── 192.168.2.26
                   └─── ❌ Panel NOT running (yet)
```

---

## 📋 QUICK TROUBLESHOOTING

### "I opened port 3000 in my modem"

**Not helpful yet because:**
- Your modem can't forward to Emergent's cloud (10.208.144.125)
- Nothing is running on your VM (192.168.2.26) to forward to

**Solution:** Deploy to your VM first, then port forwarding will work.

### "I opened UFW firewall"

**Good, but:**
- Did you open it on your VM (192.168.2.26)? That's where you need it.
- Opening it on Emergent cloud won't help access from outside.

**Verify:**
```bash
# On your VM (192.168.2.26)
ssh mike@192.168.2.26
sudo ufw status
```

Should show:
```
3000/tcp                   ALLOW       Anywhere
8001/tcp                   ALLOW       Anywhere
```

### "localhost:3000 doesn't work"

**Question:** Where are you trying this?

- **On Emergent cloud server?** ✅ Should work (it does!)
- **On your desktop?** ❌ Won't work (localhost = your desktop, not the server)
- **On your VM?** ❌ Won't work (nothing running there yet)

---

## ✅ WHAT TO DO RIGHT NOW

### Immediate Access (Today)

**Find your Emergent preview URL:**

1. Go to Emergent dashboard
2. Look for your project
3. Find "Preview" or "Live" URL
4. Use that URL to access the panel

**OR**

Contact Emergent support and ask:
"What is my preview URL for the Tactical Panel project?"

### Permanent Solution (This Week)

**Deploy to your VM using Solution B above** (Step-by-step guide provided)

After deployment:
- Access locally: `http://192.168.2.26:3000`
- Access from internet: Setup port forwarding on your modem
- Production ready: Your own server, your own control

---

## 🎯 SUMMARY

| Location | IP Address | Panel Status | How to Access |
|----------|------------|--------------|---------------|
| **Emergent Cloud** | 10.208.144.125 | ✅ RUNNING | Emergent Preview URL |
| **Your Local VM** | 192.168.2.26 | ❌ NOT INSTALLED | Deploy first (Solution B) |
| **Your Desktop** | 192.168.2.x | ❌ N/A | Access via server URLs |

---

## 📞 NEED HELP?

**Can't find Emergent preview URL?**
- Contact Emergent support
- Check Emergent dashboard
- Look for "Preview" or "Live" link in your project

**Want to deploy to your VM?**
- Follow Solution B above
- Reference: LOCAL_VM_DEPLOYMENT.md
- Estimated time: 15-30 minutes

**Still stuck?**
Run diagnostics and share:
```bash
# On Emergent cloud
hostname -I
sudo supervisorctl status
curl -I http://localhost:3000

# On your VM (after SSH)
hostname -I
sudo systemctl status tactical-backend tactical-frontend 2>/dev/null || echo "Not installed yet"
```

---

## ⚡ QUICK WIN

**Want to see it working RIGHT NOW?**

1. **Access Emergent preview URL** (ask support for the URL)
2. **Done!** Your panel is already running there.

**Want to use your own VM?**

1. Follow Solution B deployment steps
2. Takes 15-30 minutes
3. Full control on your infrastructure

---

The key takeaway: **Your panel IS working and running on Emergent's cloud (10.208.144.125). You just need to find the correct URL to access it, OR deploy it to your local VM (192.168.2.26) to access it there.**
