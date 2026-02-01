# Changelog

All notable changes to the Tactical Command panel will be documented in this file.

## [Current Fork] - 2025-02-01

### Added - Major Feature Enhancements

#### Guided Onboarding System 🆕
- **Interactive onboarding tour** for first-time admins after login
- **7-step guided walkthrough** covering:
  - Welcome and feature overview
  - SteamCMD installation guide
  - Adding first server instance
  - Resource management explanation
  - Sub-admin management introduction
  - Server controls and features tour
  - Quick reference for next steps
- **Auto-triggers** on first login (can be skipped)
- **Re-launchable** from profile menu anytime
- **Progress tracking** with visual progress bar

#### Sub-Admin Management System 🆕
- **Create sub-admin accounts** with granular permissions
- **Server-specific access control** - assign admins to specific servers
- **Permission levels**: start, stop, restart, config editing
- **Parent-child relationship** tracking
- **Full CRUD operations** via dedicated management modal
- **Backend API endpoints**: `/api/admin/sub-admins/*`

#### Resource Management System 🆕
- **Per-server resource allocation**:
  - CPU cores (1-16 cores)
  - RAM (1-64 GB)
  - Storage limits (GB)
  - Network bandwidth (Mbps)
- **Visual sliders** with numeric inputs for easy configuration
- **Real-time updates** via PATCH endpoint
- **Resource monitoring** integrated with system resources display

#### Enhanced VM Deployment Guide 🆕
- **COMPLETE_VM_DEPLOYMENT_GUIDE.md** - Comprehensive 15+ page guide
- **Critical clarification**: Emergent cloud environment vs local VM deployment
- **Step-by-step instructions** for deploying to Ubuntu Server VM
- **Troubleshooting section** covering 5 common deployment issues
- **Network configuration** for local VM access
- **Security considerations** and firewall setup
- **File locations** and service management commands

### Changed

#### Installation & Deployment
- **Dynamic systemd service generation** - no more hardcoded paths
- **Auto-detects** Python venv location (`/root/.venv` or `backend/venv`)
- **Auto-detects** application root directory
- **setup-systemd.sh** now creates service files on-the-fly with correct paths
- **Improved error messages** with actionable troubleshooting steps

#### Backend Improvements
- **Fixed** ResourceManagementModal to use PATCH instead of PUT
- **Added** resource fields to ServerInstance model (cpu_cores, ram_gb, storage_gb, network_speed_mbps)
- **Enhanced** server update endpoint to handle resource allocations
- **Improved** sub-admin permission checking in server operations

#### Frontend Improvements
- **Added** OnboardingModal component with modern UI
- **Added** Sub-Admin management button to dashboard header
- **Added** Resource management button to each server card
- **Integrated** onboarding launch on first login
- **Enhanced** dashboard with better state management

#### Documentation Updates
- **Updated** DOCUMENTATION_INDEX.md with new guide
- **Added** troubleshooting for systemd service failures
- **Added** VM-specific deployment instructions
- **Added** network configuration examples for local VMs
- **Clarified** the difference between Emergent dev environment and local deployment

### Fixed - Permission Issues (Latest)
- **Fixed:** update-panel.sh permission denied error when running from installer
- **Fixed:** Install script now ensures update-panel.sh is executable before running
- **Fixed:** fix-permissions.sh now explicitly makes all .sh files executable using find command
- **Improved:** Better error handling for permission issues in installer

### Fixed - Systemd Service Issues
- **Fixed:** Hardcoded `/app` paths in systemd service files
- **Fixed:** Incorrect user (`www-data` instead of `root`) in service files
- **Fixed:** Wrong venv path (`/app/backend/venv` instead of `/root/.venv`)
- **Fixed:** Services now work correctly on local VM deployments
- **Improved:** Dynamic path resolution based on actual installation location

### Added - Automatic Dependency Installation
- **Auto-install Python 3**: The installer now automatically installs Python 3.11+ if missing
- **Auto-install Node.js**: The installer now automatically installs Node.js 18.x if missing
- **Distribution Support**: Works on Debian/Ubuntu and RHEL/CentOS systems
- **User Prompts**: Always asks user before installing any dependencies
- **NodeSource Integration**: Uses official NodeSource repository for latest Node.js versions
- **Verification**: Verifies successful installation before proceeding

### Changed
- Updated `install-functions.sh` to include dependency auto-installation logic
- Enhanced `README.md` to mention automatic dependency installation
- Updated `INSTALLATION_GUIDE.md` with detailed auto-install information
- Updated `INSTALLER_GUIDE.md` with new installation flow examples
- **IMPORTANT**: All documentation now correctly states to use `sudo bash ./install.sh` instead of just `./install.sh`
- Updated `fix-permissions.sh` output message to show correct command

### Fixed
- Resolved "Node.js is required but not installed" error blocking installation
- Resolved "Python 3 is required but not installed" error blocking installation
- User no longer needs to manually install dependencies before running install.sh
- Clarified that installer must be run with `sudo bash ./install.sh` to avoid permission errors

---

## [Previous] - Initial Release

### Added
- Interactive menu-driven installer
- Docker and Docker Compose installation support
- Native panel installation with guided setup
- SSL/Let's Encrypt certificate installation
- SteamCMD integration
- JWT-based authentication
- Two-factor authentication (TOTP)
- Password reset via security questions
- Session timeout mechanism
- Server instance management
- Real-time resource monitoring
- Configuration editor
- Mod management
- Log viewer
- Backup and restore scripts
- Systemd service files
- Comprehensive documentation
