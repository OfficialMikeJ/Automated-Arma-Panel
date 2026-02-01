# Changelog

All notable changes to the Tactical Command panel will be documented in this file.

## [Unreleased]

### Added - Automatic Dependency Installation (Latest)
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
