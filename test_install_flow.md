# Installation Flow Test Scenarios

## Scenario 1: Fresh Ubuntu 24.04 Server (No Dependencies)

### Before Fix:
```
user@server:~$ cd /app/scripts
user@server:/app/scripts$ ./install.sh

Step 1: Checking system requirements...
[ERROR] ✗ Python 3 is required but not installed
[ERROR] ✗ Node.js is required but not installed
[ERROR] Missing dependencies. Please install Python 3.11+ and Node.js 16+ first.

Press Enter to continue...
```
**Result:** Installation blocked ❌

### After Fix:
```
user@server:~$ cd /app/scripts
user@server:/app/scripts$ ./install.sh

Step 1: Checking system requirements...
[WARNING] ✗ Python 3 is not installed
[WARNING] ✗ Node.js is not installed

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
```
**Result:** Installation continues ✅

---

## Scenario 2: System with Python but No Node.js

### After Fix:
```
Step 1: Checking system requirements...
✓ Python: 3.11.2
[WARNING] ✗ Node.js is not installed

Missing dependencies detected!

Would you like to install missing dependencies automatically? (Y/n): Y

Installing Node.js...
[INFO] Adding NodeSource repository...
✓ Node.js installed

✓ All dependencies installed successfully!
Node.js: v18.17.0
```
**Result:** Only Node.js is installed ✅

---

## Scenario 3: User Declines Auto-Install

### After Fix:
```
Step 1: Checking system requirements...
[WARNING] ✗ Python 3 is not installed
[WARNING] ✗ Node.js is not installed

Missing dependencies detected!

Would you like to install missing dependencies automatically? (Y/n): n

[ERROR] Installation cancelled. Please install Python 3.11+ and Node.js 16+ manually.

Press Enter to continue...
```
**Result:** User can install manually ✅

---

## Scenario 4: All Dependencies Already Installed

### After Fix:
```
Step 1: Checking system requirements...
✓ Python: 3.11.2
✓ Node.js: v18.17.0

Step 2: Installing MongoDB...
```
**Result:** Skips dependency installation ✅

---

## Key Improvements

1. **Automatic Detection**: Detects missing Python 3 or Node.js
2. **User Choice**: Always asks before installing
3. **Selective Installation**: Only installs what's missing
4. **Verification**: Confirms installation succeeded
5. **Multi-Distribution**: Works on Debian/Ubuntu and RHEL/CentOS
6. **Clear Messaging**: Shows what's being installed and why
7. **Fallback Option**: User can still decline and install manually

