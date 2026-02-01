# Installation Script Updates - February 1, 2025

## Issues Fixed

### 1. MongoDB Repository Error (Ubuntu 24.04 Compatibility)
**Problem:** MongoDB 7.0 repository using deprecated `apt-key` and missing Ubuntu 24.04 (Noble) support.

**Fix Applied:**
- Removed deprecated `apt-key` command
- Updated to use modern GPG keyring method (`/usr/share/keyrings/`)
- Added Ubuntu 24.04 support (uses jammy repository as fallback)
- Added fallback to community MongoDB package if official repo fails
- Added service startup verification

**File:** `/app/scripts/install-functions.sh` (lines ~160-210)

---

### 2. Missing python3-venv Package
**Problem:** Python 3 was installed but `python3-venv` package was missing, causing virtual environment creation to fail.

**Fix Applied:**
- Added explicit check for `python3-venv` package during system requirements check
- Auto-installs `python3-venv` if missing (when Python auto-install is triggered)
- Added explicit installation check before creating virtual environment in backend setup
- Added error handling with clear error message if venv creation fails

**Files Modified:**
- `/app/scripts/install-functions.sh` (lines ~40-50 for detection)
- `/app/scripts/install-functions.sh` (lines ~225-240 for backend setup)

---

## Updated Installation Flow

### Step 1: System Requirements Check
```
- Python 3.x detection
- python3-venv package detection ✅ NEW
- Node.js detection
- Yarn detection
```

### Step 2: Auto-Install Missing Dependencies
```
- If Python or python3-venv missing:
  → sudo apt-get install -y python3 python3-pip python3-venv ✅ UPDATED
  
- If Node.js missing:
  → Install Node.js 18.x from NodeSource repository
```

### Step 3: MongoDB Installation
```
- Uses modern GPG keyring method ✅ UPDATED
- Ubuntu 24.04 compatible ✅ NEW
- Fallback to community package ✅ NEW
- Service verification ✅ NEW
```

### Step 4: Backend Setup
```
- Checks for python3-venv before creating venv ✅ NEW
- Creates Python virtual environment
- Installs dependencies from requirements.txt
```

---

## Installation Commands for User

### On Your VM (192.168.2.26):

```bash
# 1. Update the installation scripts via WinSCP
# Copy updated files from Emergent to /home/mike/
# Then move to installation directory:

cd /home/mike
sudo cp -r scripts/* /opt/Automated-Arma-Panel-main/scripts/

# 2. Run the updated installer
cd /opt/Automated-Arma-Panel-main/scripts
sudo bash ./install.sh
```

Select **Option 2: Native Installation + Guided Setup**

The installer will now:
- ✅ Automatically detect missing python3-venv
- ✅ Install it if needed
- ✅ Install MongoDB with proper repository configuration
- ✅ Create virtual environment successfully
- ✅ Complete panel installation

---

## Manual Fix (If Needed)

If you encounter issues, you can manually install the missing package first:

```bash
sudo apt-get update
sudo apt-get install -y python3-venv
```

Then re-run the installer:

```bash
cd /opt/Automated-Arma-Panel-main/scripts
sudo bash ./install.sh
```

---

## Verification

After installation completes successfully, verify services are running:

```bash
# Check systemd services
sudo systemctl status tactical-backend
sudo systemctl status tactical-frontend

# Check if ports are listening
sudo ss -tuln | grep -E '3000|8001'

# Test backend API
curl http://localhost:8001/api/auth/check-first-run

# Test frontend
curl -I http://localhost:3000
```

Access the panel at: **http://192.168.2.26:3000**

---

## Files Modified in This Session

1. `/app/scripts/install-functions.sh`
   - Added python3-venv detection and auto-install
   - Fixed MongoDB repository configuration
   - Added Ubuntu 24.04 support
   - Improved error handling

2. `/app/scripts/setup-systemd.sh` (earlier in session)
   - Dynamic service file generation
   - Auto-detects installation paths

3. `/app/frontend/src/components/ResourceManagementModal.js` (earlier in session)
   - Fixed HTTP method (PUT → PATCH)

4. `/app/frontend/src/pages/DashboardPage.js` (earlier in session)
   - Added onboarding modal integration

5. `/app/frontend/src/components/OnboardingModal.js` (earlier in session)
   - NEW: Guided onboarding component

---

## Next Steps After Successful Installation

1. Access the panel: http://192.168.2.26:3000
2. Complete first-time setup (create admin account)
3. Experience the guided onboarding tour
4. Configure firewall (Option 4 in installer menu)
5. Add your first server instance

---

## Support

If you encounter any issues:

1. Check installation logs: `/opt/Automated-Arma-Panel-main/install.log`
2. Check service logs: `sudo journalctl -u tactical-backend -n 100`
3. Refer to: `COMPLETE_VM_DEPLOYMENT_GUIDE.md`
4. Verify permissions: `sudo chown -R mike:mike /opt/Automated-Arma-Panel-main`
