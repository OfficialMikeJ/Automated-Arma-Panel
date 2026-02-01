#!/bin/bash

###############################################################################
# Tactical Command - Permission Fix Script
#
# This script fixes permissions for Ubuntu Server LTS 24.04
# Run this if you get "Permission denied" errors
#
# Usage:
#   sudo ./fix-permissions.sh
###############################################################################

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Get the current user (not root, even if running with sudo)
ACTUAL_USER=${SUDO_USER:-$USER}

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo -e "  ${GREEN}Tactical Command - Permission Fix${NC}"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Check if running as root/sudo
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}[ERROR]${NC} This script must be run with sudo"
    echo ""
    echo "Usage: sudo ./fix-permissions.sh"
    echo ""
    exit 1
fi

echo -e "${BLUE}[INFO]${NC} Fixing permissions for user: $ACTUAL_USER"
echo ""

# Get the directory paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo -e "${BLUE}[INFO]${NC} Root directory: $ROOT_DIR"
echo ""

# Fix ownership of the entire project
echo -e "${YELLOW}[FIX]${NC} Setting ownership to $ACTUAL_USER..."
chown -R $ACTUAL_USER:$ACTUAL_USER "$ROOT_DIR"

# Fix permissions on scripts
echo -e "${YELLOW}[FIX]${NC} Making scripts executable..."
find "$SCRIPT_DIR" -name "*.sh" -type f -exec chmod +x {} \;

# Fix permissions on backend
echo -e "${YELLOW}[FIX]${NC} Fixing backend permissions..."
chmod -R 755 "$ROOT_DIR/backend"
if [ -d "$ROOT_DIR/backend/venv" ]; then
    find "$ROOT_DIR/backend/venv" -type f -name "*.so" -exec chmod +x {} \;
fi

# Fix permissions on frontend
echo -e "${YELLOW}[FIX]${NC} Fixing frontend permissions..."
chmod -R 755 "$ROOT_DIR/frontend"

# Fix permissions on scripts
chmod -R 755 "$SCRIPT_DIR"

# Ensure all shell scripts are executable
echo -e "${BLUE}[INFO]${NC} Making all scripts executable..."
find "$SCRIPT_DIR" -name "*.sh" -exec chmod +x {} \; 2>/dev/null || true

# Fix permissions on logs and backups directories
echo -e "${YELLOW}[FIX]${NC} Fixing logs and backups..."
mkdir -p "$ROOT_DIR/logs" "$ROOT_DIR/backups" /tmp/arma_servers
chown -R $ACTUAL_USER:$ACTUAL_USER "$ROOT_DIR/logs" "$ROOT_DIR/backups" /tmp/arma_servers
chmod -R 755 "$ROOT_DIR/logs" "$ROOT_DIR/backups" /tmp/arma_servers

# Fix SteamCMD if it exists
if [ -d "$HOME/steamcmd" ]; then
    echo -e "${YELLOW}[FIX]${NC} Fixing SteamCMD permissions..."
    chown -R $ACTUAL_USER:$ACTUAL_USER "$HOME/steamcmd"
    if [ -f "$HOME/steamcmd/steamcmd.sh" ]; then
        chmod +x "$HOME/steamcmd/steamcmd.sh"
    fi
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo -e "  ${GREEN}Permission Fix Complete!${NC}"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo -e "${GREEN}✓${NC} All files now owned by: $ACTUAL_USER"
echo -e "${GREEN}✓${NC} Scripts are executable"
echo -e "${GREEN}✓${NC} Directories have correct permissions"
echo ""
echo "You can now run the installer:"
echo -e "  ${BLUE}cd $SCRIPT_DIR${NC}"
echo -e "  ${BLUE}sudo bash ./install.sh${NC}"
echo ""
echo -e "${YELLOW}Note:${NC} Always use 'sudo bash ./install.sh' - do NOT use just './install.sh'"
echo ""
