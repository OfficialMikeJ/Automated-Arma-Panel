# Installation Script Guide

Visual guide for the Tactical Command interactive installer.

## Menu Structure

```
┌────────────────────────────────────────────────────────────┐
│        TACTICAL COMMAND - Interactive Installer            │
│                                                             │
│  Installation Status:                                      │
│    ✓/✗ Docker                                             │
│    ✓/✗ Docker Compose                                     │
│    ✓/✗ MongoDB                                            │
│    ✓/✗ Panel                                              │
│                                                             │
│  Installation Options:                                     │
│                                                             │
│    1) Install Docker & Docker Compose                      │
│       • Auto-detects existing installations                │
│       • Downloads latest versions                          │
│       • Configures user permissions                        │
│                                                             │
│    2) Install Panel - Native + Guided Setup                │
│       • Checks system requirements                         │
│       • Installs MongoDB (optional)                        │
│       • Sets up Python backend                             │
│       • Sets up React frontend                             │
│       • Guided configuration wizard                        │
│                                                             │
│    3) Install SSL Certificates (Let's Encrypt)             │
│       • Installs Certbot                                   │
│       • Configures nginx                                   │
│       • Obtains SSL certificate                            │
│       • Sets up auto-renewal                               │
│                                                             │
│    4) Restart Installation                                 │
│       • Re-detects system state                            │
│       • Updates installation status                        │
│                                                             │
│    5) Exit Installer                                       │
│       • Shows quick start guide                            │
│       • Displays next steps                                │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

## Usage Modes

### 1. Interactive Mode (Default)

```bash
cd /app/scripts
sudo bash ./install.sh
```

**Important:** Always use `sudo bash` - using just `./install.sh` will fail with permission errors.

**Features:**
- Main menu with 5 options
- Auto-detection of installed components
- Visual status indicators
- Guided step-by-step process
- Color-coded output
- Progress feedback

**Best For:**
- First-time installation
- Custom setup requirements
- Learning the installation process
- Selective component installation

### 2. Automatic Mode

```bash
cd /app/scripts
sudo bash ./install.sh --auto
```

**Features:**
- One-command installation
- Minimal user interaction
- Installs both Docker and Native
- Uses sensible defaults
- Fast deployment

**Best For:**
- Quick setup
- Experienced users
- CI/CD automation
- Repeated installations

## Option Details

### Option 1: Install Docker & Docker Compose

**What it does:**
1. Detects if Docker/Docker Compose already installed
2. Downloads Docker install script from get.docker.com
3. Installs Docker Engine
4. Adds current user to docker group
5. Downloads latest Docker Compose from GitHub
6. Installs to /usr/local/bin/docker-compose
7. Verifies installation

**Output:**
```
═══════════════════════════════════════════════════════════════
  OPTION 1: Install Docker & Docker Compose
═══════════════════════════════════════════════════════════════

[INFO] Detecting existing installations...
✓ Docker not installed
✗ Docker Compose not installed

[INFO] Installing Docker...
[... installation progress ...]
✓ Docker installed successfully

[INFO] Installing Docker Compose...
[... installation progress ...]
✓ Docker Compose installed successfully

[SUCCESS] Docker installation complete!

Important: You may need to log out and back in
```

**Requirements:**
- Internet connection
- sudo access
- ~1GB disk space

**Time:** 2-5 minutes

---

### Option 2: Install Panel - Native + Guided Setup

**What it does:**

**Step 1: System Check (Auto-Install)**
- ✅ **NEW**: Auto-installs Python 3 if missing
- ✅ **NEW**: Auto-installs Node.js 18.x if missing
- Verifies Python 3.11+
- Verifies Node.js 16+
- Checks for Yarn
- Detects MongoDB

**Automatic Dependency Installation:**
- Detects Debian/Ubuntu or RHEL/CentOS
- Uses NodeSource repository for Node.js 18.x
- Installs Python 3, pip, and venv packages
- Prompts user before installation
- Verifies successful installation

**Step 2: MongoDB Setup**
- Offers to install MongoDB locally
- Auto-detects distribution (Ubuntu/Debian)
- Starts and enables MongoDB service

**Step 3: Backend Setup**
- Creates Python virtual environment
- Upgrades pip
- Installs all Python dependencies
- Configures backend .env

**Step 4: Frontend Setup**
- Installs Yarn if needed
- Installs Node.js dependencies
- Configures frontend .env

**Step 5: Guided Configuration**
- MongoDB URL (default: mongodb://localhost:27017)
- Database name (default: arma_server_panel)
- Backend URL (default: http://localhost:8001)
- Auto-generates security keys
- Creates necessary directories

**Output:**
```
═══════════════════════════════════════════════════════════════
  OPTION 2: Native Installation + Guided Setup
═══════════════════════════════════════════════════════════════

Step 1: Checking system requirements...
✗ Python 3 is not installed
✗ Node.js is not installed

Missing dependencies detected!

Would you like to install missing dependencies automatically? (Y/n): Y

Installing Python 3...
[INFO] Adding repositories...
✓ Python 3 installed

Installing Node.js...
[INFO] Adding NodeSource repository...
✓ Node.js installed

✓ All dependencies installed successfully!
Python: 3.11.2
Node.js: v18.17.0

Step 2: Installing MongoDB...
[... installation progress ...]
✓ MongoDB installed and started

Step 3: Setting up backend...
[... installation progress ...]
✓ Backend setup complete

Step 4: Setting up frontend...
[... installation progress ...]
✓ Frontend setup complete

Step 5: Configuration Setup
MongoDB URL [mongodb://localhost:27017]: 
Database name [arma_server_panel]: 
Backend URL [http://localhost:8001]: 

✓ Backend configured
✓ Frontend configured
✓ Directories created

[SUCCESS] Native installation complete!
```

**Requirements:**
- Python 3.11+
- Node.js 16+
- 2GB RAM
- 2GB disk space

**Time:** 5-10 minutes

---

### Option 3: Install SSL Certificates (Let's Encrypt)

**What it does:**

**Pre-checks:**
- Verifies domain points to server
- Checks ports 80/443 accessibility
- Validates email address

**Installation:**
1. Installs Certbot and nginx plugin
2. Installs nginx if not present
3. Creates nginx configuration for domain
4. Enables site configuration
5. Obtains SSL certificate from Let's Encrypt
6. Configures HTTPS redirect
7. Sets up auto-renewal

**Output:**
```
═══════════════════════════════════════════════════════════════
  OPTION 3: Install SSL Certificates (Let's Encrypt)
═══════════════════════════════════════════════════════════════

[WARNING] SSL Certificate Setup

Requirements:
  • Domain name pointing to this server
  • Ports 80 and 443 accessible from internet
  • Valid email address for Let's Encrypt

Continue with SSL setup? (y/N): y

Enter your domain name: panel.yourdomain.com
Enter your email address: admin@yourdomain.com

[INFO] Installing Certbot...
✓ Certbot installed

[INFO] Configuring nginx...
✓ nginx configured

[INFO] Requesting SSL certificate...
[... Let's Encrypt process ...]
✓ SSL certificate installed successfully!

Your panel is now accessible at: https://panel.yourdomain.com

✓ Auto-renewal test passed
```

**Requirements:**
- Domain name (A record pointing to server)
- Open ports 80, 443
- Valid email address
- nginx web server

**Time:** 2-3 minutes

---

### Option 4: Restart Installation

**What it does:**
- Clears current detection state
- Re-scans system for components
- Updates status display
- Refreshes menu

**Use Cases:**
- After manual installation of components
- To verify installation success
- After fixing issues
- To update status display

---

### Option 5: Exit Installer

**What it does:**
1. Shows quick start guide
2. Displays appropriate commands based on installed components
3. Shows Docker commands (if installed)
4. Shows native commands (if installed)
5. Lists production deployment options
6. Provides documentation links

## Color Coding

The installer uses colors for clarity:

- 🟢 **GREEN** - Success messages, installed components
- 🔴 **RED** - Errors, not installed components
- 🟡 **YELLOW** - Warnings, prompts
- 🔵 **BLUE** - Information, progress
- 🟣 **CYAN** - Headers, commands, URLs
- 🟣 **MAGENTA** - Section titles

## Logging

All installation activities are logged to:
```
/app/install.log
```

View log:
```bash
tail -f /app/install.log
```

## Error Handling

The installer includes robust error handling:

- Checks before installation
- Validates user input
- Provides helpful error messages
- Suggests fixes for common issues
- Allows retry without losing progress

## Common Workflows

### First-Time Setup (Docker)

```bash
./install.sh

# Select Option 1 (Install Docker)
# Select Option 5 (Exit)
# Follow Docker quick start guide
```

### First-Time Setup (Native)

```bash
./install.sh

# Select Option 2 (Install Panel)
# Answer configuration questions
# Select Option 5 (Exit)
# Follow native quick start guide
```

### Production Setup with SSL

```bash
./install.sh

# Select Option 1 (Install Docker) OR Option 2 (Native)
# Select Option 3 (Install SSL)
# Enter domain and email
# Select Option 5 (Exit)
```

### Check Installation Status

```bash
./install.sh

# View status at top of menu
# Select Option 5 (Exit)
```

## Tips

1. **Run as regular user** - Script will use sudo when needed
2. **Keep terminal open** - Don't close during installation
3. **Read prompts carefully** - Default values shown in brackets
4. **Check status first** - Menu shows what's already installed
5. **Use Option 4** - Restart detection if status looks wrong

## Troubleshooting

**Menu doesn't appear:**
```bash
# Make sure script is executable
chmod +x install.sh

# Try again
./install.sh
```

**Colors not showing:**
```bash
# Your terminal may not support colors
# Functionality works the same
```

**Installation fails:**
```bash
# Check log file
tail -50 /app/install.log

# Try specific option again
# Or restart detection (Option 4)
```

**Docker permission errors:**
```bash
# Log out and back in after Docker installation
# Or add user to docker group manually:
sudo usermod -aG docker $USER
newgrp docker
```

## Next Steps After Installation

See the quick start guide displayed on exit, or refer to:
- `README.md` - Complete documentation
- `QUICKSTART.md` - Fast setup guide  
- `DEPLOYMENT.md` - Production deployment
- `INSTALLATION_GUIDE.md` - Installation comparison

## Support

If you encounter issues:
1. Check `/app/install.log`
2. Review error messages
3. Consult README.md troubleshooting section
4. Open GitHub issue with log output
