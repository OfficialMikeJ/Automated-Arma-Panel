#!/bin/bash

###############################################################################
# Tactical Command - Systemd Setup Script
#
# This script installs and configures systemd services for automatic startup
#
# Usage:
#   sudo ./setup-systemd.sh
###############################################################################

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Directories
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)"
SCRIPT_DIR="$ROOT_DIR/scripts"
SYSTEMD_DIR="$SCRIPT_DIR/systemd"

log() {
    echo -e "${GREEN}[SYSTEMD]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_header() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "  Tactical Command - Systemd Service Setup"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
}

check_root() {
    if [ "$EUID" -ne 0 ]; then
        error "This script must be run as root (use sudo)"
        exit 1
    fi
    log "✓ Running with root privileges"
}

check_files() {
    log "Checking service files..."
    
    if [ ! -f "$SYSTEMD_DIR/tactical-backend.service" ]; then
        error "Backend service file not found"
        exit 1
    fi
    
    if [ ! -f "$SYSTEMD_DIR/tactical-frontend.service" ]; then
        error "Frontend service file not found"
        exit 1
    fi
    
    log "✓ Service files found"
}

create_user() {
    log "Creating/checking www-data user..."
    
    if id "www-data" &>/dev/null; then
        log "✓ User www-data already exists"
    else
        useradd -r -s /bin/false www-data
        log "✓ Created www-data user"
    fi
}

set_permissions() {
    log "Setting file permissions..."
    
    # Backend directory
    chown -R www-data:www-data "$ROOT_DIR/backend"
    chmod -R 755 "$ROOT_DIR/backend"
    
    # Frontend directory
    chown -R www-data:www-data "$ROOT_DIR/frontend"
    chmod -R 755 "$ROOT_DIR/frontend"
    
    # Server data directory
    mkdir -p /tmp/arma_servers
    chown -R www-data:www-data /tmp/arma_servers
    chmod -R 755 /tmp/arma_servers
    
    # Logs directory
    mkdir -p "$ROOT_DIR/logs"
    chown -R www-data:www-data "$ROOT_DIR/logs"
    chmod -R 755 "$ROOT_DIR/logs"
    
    log "✓ Permissions set"
}

install_services() {
    log "Installing systemd services..."
    
    # Copy service files
    cp "$SYSTEMD_DIR/tactical-backend.service" /etc/systemd/system/
    cp "$SYSTEMD_DIR/tactical-frontend.service" /etc/systemd/system/
    
    # Reload systemd
    systemctl daemon-reload
    
    log "✓ Services installed"
}

enable_services() {
    log "Enabling services for auto-start..."
    
    systemctl enable tactical-backend.service
    systemctl enable tactical-frontend.service
    
    log "✓ Services enabled"
}

start_services() {
    log "Starting services..."
    
    systemctl start tactical-backend.service
    systemctl start tactical-frontend.service
    
    sleep 2
    
    # Check status
    if systemctl is-active --quiet tactical-backend; then
        log "✓ Backend service started"
    else
        error "Backend service failed to start"
        systemctl status tactical-backend.service --no-pager -l
        exit 1
    fi
    
    if systemctl is-active --quiet tactical-frontend; then
        log "✓ Frontend service started"
    else
        error "Frontend service failed to start"
        systemctl status tactical-frontend.service --no-pager -l
        exit 1
    fi
}

print_summary() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo -e "  ${GREEN}Systemd Setup Complete!${NC}"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    echo "Services installed and started:"
    echo "  • tactical-backend.service  - Backend API server"
    echo "  • tactical-frontend.service - Frontend web server"
    echo ""
    echo "Service Management Commands:"
    echo ""
    echo "  Status:"
    echo "    sudo systemctl status tactical-backend"
    echo "    sudo systemctl status tactical-frontend"
    echo ""
    echo "  Start:"
    echo "    sudo systemctl start tactical-backend"
    echo "    sudo systemctl start tactical-frontend"
    echo ""
    echo "  Stop:"
    echo "    sudo systemctl stop tactical-backend"
    echo "    sudo systemctl stop tactical-frontend"
    echo ""
    echo "  Restart:"
    echo "    sudo systemctl restart tactical-backend"
    echo "    sudo systemctl restart tactical-frontend"
    echo ""
    echo "  View Logs:"
    echo "    sudo journalctl -u tactical-backend -f"
    echo "    sudo journalctl -u tactical-frontend -f"
    echo ""
    echo "  Disable Auto-start:"
    echo "    sudo systemctl disable tactical-backend"
    echo "    sudo systemctl disable tactical-frontend"
    echo ""
    echo "Access the panel at: http://localhost:3000"
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
}

main() {
    print_header
    
    check_root
    check_files
    create_user
    set_permissions
    install_services
    enable_services
    start_services
    
    print_summary
    
    log "Setup completed successfully!"
}

# Run main
main "$@"
