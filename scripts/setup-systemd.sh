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
    
    # Determine Python venv path
    VENV_PATH="/root/.venv"
    if [ ! -f "$VENV_PATH/bin/python3" ]; then
        warn "Python venv not found at $VENV_PATH, checking backend/venv..."
        VENV_PATH="$ROOT_DIR/backend/venv"
        if [ ! -f "$VENV_PATH/bin/python3" ]; then
            error "Could not find Python virtual environment!"
            exit 1
        fi
    fi
    
    log "Using Python venv: $VENV_PATH"
    log "Application path: $ROOT_DIR"
    
    # Create backend service with dynamic paths
    cat > /etc/systemd/system/tactical-backend.service << EOF
[Unit]
Description=Tactical Command Backend Service
After=network.target mongodb.service
Wants=mongodb.service

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=$ROOT_DIR/backend

# Virtual environment activation and start
ExecStart=$VENV_PATH/bin/python -m uvicorn server:app --host 0.0.0.0 --port 8001 --workers 1

# Restart policy
Restart=always
RestartSec=10

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=tactical-backend

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
EOF
    
    # Create frontend service with dynamic paths
    cat > /etc/systemd/system/tactical-frontend.service << EOF
[Unit]
Description=Tactical Command Frontend Service
After=network.target tactical-backend.service
Wants=tactical-backend.service

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=$ROOT_DIR/frontend

# Environment
Environment="HOST=0.0.0.0"
Environment="PORT=3000"

# Start command
ExecStart=/usr/bin/yarn start

# Restart policy
Restart=always
RestartSec=10

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=tactical-frontend

# Resource limits
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd
    systemctl daemon-reload
    
    log "✓ Services installed with paths:"
    log "  Backend: $ROOT_DIR/backend"
    log "  Frontend: $ROOT_DIR/frontend"
    log "  Python: $VENV_PATH/bin/uvicorn"
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
