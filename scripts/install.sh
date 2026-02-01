#!/bin/bash

###############################################################################
# Tactical Command - Arma Server Management Panel
# Interactive Installation Script
#
# This script provides a guided installation experience with multiple options.
#
# IMPORTANT: Always run with sudo bash
#   sudo bash ./install.sh           # Interactive menu (default)
#   sudo bash ./install.sh --auto    # Quick automatic installation
#   sudo bash ./install.sh --help    # Show help
#
# Do NOT use just ./install.sh - it will fail with permission errors
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Installation mode
INSTALL_MODE="interactive"

# Directories
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
SCRIPTS_DIR="$ROOT_DIR/scripts"

# Log file
LOG_FILE="$ROOT_DIR/install.log"

# Installation state
DOCKER_INSTALLED=false
DOCKER_COMPOSE_INSTALLED=false
MONGODB_INSTALLED=false
PANEL_INSTALLED=false

###############################################################################
# Helper Functions
###############################################################################

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

print_header() {
    clear
    echo ""
    echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                                                                   ║${NC}"
    echo -e "${CYAN}║${NC}     ${GREEN}TACTICAL COMMAND - ARMA SERVER MANAGEMENT PANEL${NC}      ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}                    ${BLUE}Interactive Installer${NC}                     ${CYAN}║${NC}"
    echo -e "${CYAN}║                                                                   ║${NC}"
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_separator() {
    echo -e "${CYAN}───────────────────────────────────────────────────────────────────${NC}"
}

check_command() {
    if command -v "$1" &> /dev/null; then
        return 0
    else
        return 1
    fi
}

pause() {
    echo ""
    read -p "Press Enter to continue..."
}

###############################################################################
# System Detection
###############################################################################

detect_installations() {
    info "Detecting existing installations..."
    
    # Check Docker
    if check_command docker; then
        DOCKER_VERSION=$(docker --version 2>/dev/null | cut -d ' ' -f3 | tr -d ',')
        DOCKER_INSTALLED=true
        success "✓ Docker detected: $DOCKER_VERSION"
    else
        warn "✗ Docker not installed"
    fi
    
    # Check Docker Compose
    if check_command docker-compose; then
        COMPOSE_VERSION=$(docker-compose --version 2>/dev/null | cut -d ' ' -f3 | tr -d ',')
        DOCKER_COMPOSE_INSTALLED=true
        success "✓ Docker Compose detected: $COMPOSE_VERSION"
    else
        warn "✗ Docker Compose not installed"
    fi
    
    # Check MongoDB
    if check_command mongod; then
        MONGODB_INSTALLED=true
        success "✓ MongoDB detected"
    else
        warn "✗ MongoDB not installed"
    fi
    
    # Check if panel is installed
    if [ -f "$BACKEND_DIR/venv/bin/activate" ] && [ -d "$FRONTEND_DIR/node_modules" ]; then
        PANEL_INSTALLED=true
        success "✓ Panel components detected"
    else
        warn "✗ Panel not fully installed"
    fi
    
    echo ""
}

###############################################################################
# Docker Installation (Option 1)
###############################################################################

install_docker_and_compose() {
    print_header
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${MAGENTA}  OPTION 1: Install Docker & Docker Compose${NC}"
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    detect_installations
    
    if [ "$DOCKER_INSTALLED" = true ] && [ "$DOCKER_COMPOSE_INSTALLED" = true ]; then
        success "Docker and Docker Compose are already installed!"
        echo ""
        info "Current versions:"
        echo "  • Docker: $DOCKER_VERSION"
        echo "  • Docker Compose: $COMPOSE_VERSION"
        echo ""
        read -p "Do you want to reinstall/update? (y/N): " -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            info "Skipping Docker installation"
            pause
            return 0
        fi
    fi
    
    log "Starting Docker installation..."
    echo ""
    
    # Install Docker
    if [ "$DOCKER_INSTALLED" = false ]; then
        info "Installing Docker..."
        echo ""
        
        # Download and run Docker install script
        curl -fsSL https://get.docker.com -o /tmp/get-docker.sh
        
        if [ $? -eq 0 ]; then
            sudo sh /tmp/get-docker.sh
            rm /tmp/get-docker.sh
            
            # Add current user to docker group
            sudo usermod -aG docker $USER
            
            success "✓ Docker installed successfully"
            DOCKER_INSTALLED=true
        else
            error "Failed to download Docker installation script"
            pause
            return 1
        fi
    else
        info "Docker already installed, skipping..."
    fi
    
    echo ""
    
    # Install Docker Compose
    if [ "$DOCKER_COMPOSE_INSTALLED" = false ]; then
        info "Installing Docker Compose..."
        echo ""
        
        # Get latest version
        COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d'"' -f4)
        
        # Download Docker Compose
        sudo curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        
        # Make executable
        sudo chmod +x /usr/local/bin/docker-compose
        
        # Verify installation
        if docker-compose --version &> /dev/null; then
            success "✓ Docker Compose installed successfully"
            DOCKER_COMPOSE_INSTALLED=true
        else
            error "Failed to install Docker Compose"
            pause
            return 1
        fi
    else
        info "Docker Compose already installed, skipping..."
    fi
    
    echo ""
    print_separator
    echo ""
    success "Docker installation complete!"
    echo ""
    info "Important: You may need to log out and back in for group permissions to take effect"
    echo ""
    info "Test Docker installation with:"
    echo "  ${CYAN}docker --version${NC}"
    echo "  ${CYAN}docker-compose --version${NC}"
    echo "  ${CYAN}docker run hello-world${NC}"
    echo ""
    
    pause
}

###############################################################################
# Main Menu
###############################################################################

show_main_menu() {
    while true; do
        print_header
        
        # Show installation status
        echo -e "${CYAN}Installation Status:${NC}"
        echo ""
        if [ "$DOCKER_INSTALLED" = true ]; then
            echo -e "  ${GREEN}✓${NC} Docker: ${GREEN}Installed${NC}"
        else
            echo -e "  ${RED}✗${NC} Docker: ${RED}Not Installed${NC}"
        fi
        
        if [ "$DOCKER_COMPOSE_INSTALLED" = true ]; then
            echo -e "  ${GREEN}✓${NC} Docker Compose: ${GREEN}Installed${NC}"
        else
            echo -e "  ${RED}✗${NC} Docker Compose: ${RED}Not Installed${NC}"
        fi
        
        if [ "$MONGODB_INSTALLED" = true ]; then
            echo -e "  ${GREEN}✓${NC} MongoDB: ${GREEN}Installed${NC}"
        else
            echo -e "  ${RED}✗${NC} MongoDB: ${RED}Not Installed${NC}"
        fi
        
        if [ "$PANEL_INSTALLED" = true ]; then
            echo -e "  ${GREEN}✓${NC} Panel: ${GREEN}Installed${NC}"
        else
            echo -e "  ${RED}✗${NC} Panel: ${RED}Not Installed${NC}"
        fi
        
        echo ""
        print_separator
        echo ""
        echo -e "${CYAN}Installation Options:${NC}"
        echo ""
        echo -e "  ${GREEN}1${NC}) Install Docker & Docker Compose (Latest Versions)"
        echo -e "  ${GREEN}2${NC}) Install Panel - Native Installation + Guided Setup"
        echo -e "  ${GREEN}3${NC}) Install SSL Certificates (Let's Encrypt)"
        echo -e "  ${GREEN}4${NC}) Configure Firewall (UFW) - Secure Your Server"
        echo -e "  ${GREEN}5${NC}) Update Panel - Install Updates & Patches"
        echo -e "  ${GREEN}6${NC}) Restart Installation (Re-detect System)"
        echo -e "  ${GREEN}7${NC}) Exit Installer"
        echo ""
        print_separator
        echo ""
        read -p "Select option [1-7]: " choice
        
        case $choice in
            1)
                install_docker_and_compose
                detect_installations
                ;;
            2)
                install_native_panel
                detect_installations
                ;;
            3)
                install_ssl_certificates
                ;;
            4)
                configure_firewall
                ;;
            5)
                # Make sure update script is executable
                chmod +x "$SCRIPTS_DIR/update-panel.sh" 2>/dev/null || true
                bash "$SCRIPTS_DIR/update-panel.sh"
                ;;
            6)
                log "Restarting installation..."
                detect_installations
                success "System re-detected!"
                pause
                ;;
            7)
                echo ""
                info "Exiting installer..."
                echo ""
                if [ "$PANEL_INSTALLED" = true ]; then
                    print_quick_start
                fi
                echo ""
                exit 0
                ;;
            *)
                error "Invalid option. Please select 1-7."
                pause
                ;;
        esac
    done
}

###############################################################################
# Quick Start Guide
###############################################################################

print_quick_start() {
    echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}                         ${GREEN}Quick Start Guide${NC}                        ${CYAN}║${NC}"
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    if [ "$DOCKER_INSTALLED" = true ] && [ "$DOCKER_COMPOSE_INSTALLED" = true ]; then
        echo -e "${YELLOW}Option A: Start with Docker${NC}"
        echo ""
        echo "  1. Deploy with Docker Compose:"
        echo -e "     ${CYAN}cd $ROOT_DIR${NC}"
        echo -e "     ${CYAN}docker-compose up -d${NC}"
        echo ""
        echo "  2. View logs:"
        echo -e "     ${CYAN}docker-compose logs -f${NC}"
        echo ""
        echo "  3. Access panel:"
        echo -e "     ${CYAN}http://localhost:3000${NC}"
        echo ""
        print_separator
        echo ""
    fi
    
    if [ "$PANEL_INSTALLED" = true ]; then
        echo -e "${YELLOW}Option B: Start with Native Installation${NC}"
        echo ""
        echo "  1. Start MongoDB:"
        echo -e "     ${CYAN}sudo systemctl start mongod${NC}"
        echo ""
        echo "  2. Start backend (Terminal 1):"
        echo -e "     ${CYAN}cd $BACKEND_DIR${NC}"
        echo -e "     ${CYAN}source venv/bin/activate${NC}"
        echo -e "     ${CYAN}uvicorn server:app --host 0.0.0.0 --port 8001 --reload${NC}"
        echo ""
        echo "  3. Start frontend (Terminal 2):"
        echo -e "     ${CYAN}cd $FRONTEND_DIR${NC}"
        echo -e "     ${CYAN}yarn start${NC}"
        echo ""
        echo "  4. Access panel:"
        echo -e "     ${CYAN}http://localhost:3000${NC}"
        echo ""
        print_separator
        echo ""
    fi
    
    echo -e "${YELLOW}Production Deployment:${NC}"
    echo ""
    echo "  • Setup systemd services:"
    echo -e "    ${CYAN}sudo ./scripts/setup-systemd.sh${NC}"
    echo ""
    echo "  • Enable backups:"
    echo -e "    ${CYAN}./scripts/backup.sh${NC}"
    echo ""
    echo "  • View full documentation:"
    echo -e "    ${CYAN}README.md, DEPLOYMENT.md, QUICKSTART.md${NC}"
    echo ""
}

install_yarn() {
    if ! command -v yarn &> /dev/null; then
        log "Installing Yarn..."
        npm install -g yarn || {
            error "Failed to install Yarn"
            exit 1
        }
        log "✓ Yarn installed successfully"
    fi
}

install_mongodb() {
    if ! command -v mongod &> /dev/null; then
        log "Installing MongoDB..."
        
        # Detect distribution
        if [ -f /etc/debian_version ]; then
            # Debian/Ubuntu
            sudo apt-get update
            sudo apt-get install -y mongodb-org || sudo apt-get install -y mongodb
        elif [ -f /etc/redhat-release ]; then
            # RedHat/CentOS
            sudo yum install -y mongodb-org
        else
            warn "Could not detect distribution. Please install MongoDB manually."
            return 1
        fi
        
        # Start MongoDB
        sudo systemctl start mongod || sudo systemctl start mongodb
        sudo systemctl enable mongod || sudo systemctl enable mongodb
        
        log "✓ MongoDB installed and started"
    fi
}

setup_backend() {
    log "Setting up backend..."
    
    cd "$BACKEND_DIR"
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        log "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    log "Upgrading pip..."
    pip install --upgrade pip
    
    # Install dependencies
    log "Installing Python dependencies..."
    pip install -r requirements.txt
    
    log "✓ Backend setup complete"
}

setup_frontend() {
    log "Setting up frontend..."
    
    cd "$FRONTEND_DIR"
    
    # Install dependencies
    log "Installing Node.js dependencies..."
    yarn install
    
    log "✓ Frontend setup complete"
}

###############################################################################
# Configuration
###############################################################################

setup_backend_env() {
    log "Configuring backend environment..."
    
    local env_file="$BACKEND_DIR/.env"
    
    if [ -f "$env_file" ] && [ "$INSTALL_MODE" = "manual" ]; then
        read -p ".env file already exists. Overwrite? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log "Keeping existing .env file"
            return
        fi
    fi
    
    # Generate random secret key
    SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 64 | head -n 1)
    
    cat > "$env_file" << EOF
# MongoDB Configuration
MONGO_URL=mongodb://localhost:27017
DB_NAME=arma_server_panel

# Security
SECRET_KEY=$SECRET_KEY

# CORS
CORS_ORIGINS=*
EOF
    
    log "✓ Backend .env configured"
}

setup_frontend_env() {
    log "Configuring frontend environment..."
    
    local env_file="$FRONTEND_DIR/.env"
    
    if [ -f "$env_file" ] && [ "$INSTALL_MODE" = "manual" ]; then
        read -p ".env file already exists. Overwrite? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log "Keeping existing .env file"
            return
        fi
    fi
    
    # Get backend URL
    if [ "$INSTALL_MODE" = "manual" ]; then
        read -p "Enter backend URL [http://localhost:8001]: " BACKEND_URL
        BACKEND_URL=${BACKEND_URL:-http://localhost:8001}
    else
        BACKEND_URL="http://localhost:8001"
    fi
    
    cat > "$env_file" << EOF
REACT_APP_BACKEND_URL=$BACKEND_URL
WDS_SOCKET_PORT=0
ENABLE_HEALTH_CHECK=false
EOF
    
    log "✓ Frontend .env configured"
}

create_directories() {
    log "Creating necessary directories..."
    
    mkdir -p /tmp/arma_servers
    mkdir -p "$ROOT_DIR/logs"
    
    log "✓ Directories created"
}

###############################################################################
# Post-Installation
###############################################################################

print_summary() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo -e "  ${GREEN}Installation Complete!${NC}"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    echo "Next steps:"
    echo ""
    echo "1. Start MongoDB (if not running):"
    echo "   sudo systemctl start mongod"
    echo ""
    echo "2. Start the backend:"
    echo "   cd $BACKEND_DIR"
    echo "   source venv/bin/activate"
    echo "   uvicorn server:app --host 0.0.0.0 --port 8001 --reload"
    echo ""
    echo "3. Start the frontend (in a new terminal):"
    echo "   cd $FRONTEND_DIR"
    echo "   yarn start"
    echo ""
    echo "4. Access the panel:"
    echo "   http://localhost:3000"
    echo ""
    echo "5. Create your admin account and start managing servers!"
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    echo "For more information, see README.md"
    echo "Installation log saved to: $LOG_FILE"
    echo ""
}

###############################################################################
# Main Installation Flow
###############################################################################

show_help() {
    cat << EOF
═══════════════════════════════════════════════════════════════
  Tactical Command - Interactive Installation Script
═══════════════════════════════════════════════════════════════

IMPORTANT: Always run with sudo bash

Usage: sudo bash $0 [OPTIONS]

OPTIONS:
    (none)      Interactive menu (default - recommended)
    --auto      Quick automatic installation
    --help      Show this help message

INTERACTIVE MODE (default):
    Run without arguments for guided installation menu:
    • Install Docker & Docker Compose
    • Install Panel (Native) with guided setup
    • Configure SSL/HTTPS certificates
    • Re-detect system state
    • Exit with quick start guide

AUTOMATIC MODE:
    Quick one-command installation:
    sudo bash $0 --auto

EXAMPLES:
    sudo bash $0                  # Interactive menu
    sudo bash $0 --auto           # Automatic installation
    $0 --help           # Show this help

FEATURES:
    ✓ Auto-detect existing installations
    ✓ Guided configuration setup
    ✓ Docker and Native installation options
    ✓ Let's Encrypt SSL support
    ✓ Production-ready setup
    ✓ Comprehensive logging

For more information, see:
    • README.md - Full documentation
    • QUICKSTART.md - Quick setup guide
    • DEPLOYMENT.md - Production deployment

═══════════════════════════════════════════════════════════════

EOF
}

quick_auto_install() {
    print_header
    log "Starting automatic installation..."
    echo ""
    
    detect_installations
    
    echo ""
    print_separator
    echo ""
    
    # Install Docker if not present
    if [ "$DOCKER_INSTALLED" = false ] || [ "$DOCKER_COMPOSE_INSTALLED" = false ]; then
        warn "Docker/Docker Compose not found"
        read -p "Install Docker & Docker Compose? (Y/n): " -r
        echo ""
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            install_docker_and_compose
            detect_installations
        fi
    fi
    
    echo ""
    print_separator
    echo ""
    
    # Install panel if not present
    if [ "$PANEL_INSTALLED" = false ]; then
        info "Installing panel natively..."
        echo ""
        
        # Source installation functions
        source "$SCRIPTS_DIR/install-functions.sh"
        
        install_native_panel
        detect_installations
    else
        success "Panel already installed!"
    fi
    
    echo ""
    print_separator
    echo ""
    
    success "Automatic installation complete!"
    echo ""
    print_quick_start
    echo ""
}

main() {
    # Source installation functions
    if [ -f "$SCRIPTS_DIR/install-functions.sh" ]; then
        source "$SCRIPTS_DIR/install-functions.sh"
    fi
    
    # Parse arguments
    case "${1:-}" in
        --auto)
            quick_auto_install
            exit 0
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        "")
            # Interactive mode (default)
            print_header
            info "Welcome to the Tactical Command installer!"
            echo ""
            info "Detecting your system..."
            echo ""
            detect_installations
            echo ""
            info "Press Enter to continue to the main menu..."
            read
            show_main_menu
            ;;
        *)
            error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"

show_docker_guide() {
    cat << EOF

═══════════════════════════════════════════════════════════════
  Docker Installation Guide
═══════════════════════════════════════════════════════════════

Docker provides an isolated, containerized deployment option.

Prerequisites:
--------------
1. Install Docker:
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh

2. Install Docker Compose:
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-\$(uname -s)-\$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose

Quick Start:
------------
1. Navigate to project directory:
   cd $ROOT_DIR

2. Start all services:
   docker-compose up -d

3. View logs:
   docker-compose logs -f

4. Access the panel:
   Frontend: http://localhost:3000
   Backend:  http://localhost:8001

Management:
-----------
• Stop services:     docker-compose down
• Restart services:  docker-compose restart
• View status:       docker-compose ps
• Update services:   docker-compose up -d --build

What's Included:
----------------
• MongoDB with persistent storage
• Backend API (FastAPI)
• Frontend (React with nginx)
• Health checks for all services
• Automatic restart on failure
• Isolated network

Benefits:
---------
✓ No dependency conflicts
✓ Easy cleanup and removal
✓ Consistent across systems
✓ Production-ready configuration
✓ Simple backup/restore with volumes

For more details, see:
• README.md - Full documentation
• DEPLOYMENT.md - Production deployment guide
• docker-compose.yml - Service configuration

═══════════════════════════════════════════════════════════════

EOF
}

main() {
    # Parse arguments
    case "${1:-}" in
        --auto)
            INSTALL_MODE="auto"
            ;;
        --manual)
            INSTALL_MODE="manual"
            ;;
        --docker)
            show_docker_guide
            exit 0
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        "")
            INSTALL_MODE="manual"
            ;;
        *)
            error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
    
    # Start installation
    print_header
    log "Starting NATIVE installation in $INSTALL_MODE mode..."
    log "Installation directory: $ROOT_DIR"
    log ""
    info "💡 Tip: For Docker deployment, run: ./install.sh --docker"
    echo ""
    
    # Check if running as root
    check_root
    
    # System requirements
    check_system_requirements
    
    # Install missing dependencies
    if [ "$INSTALL_MODE" = "auto" ]; then
        install_yarn
        install_mongodb
    else
        read -p "Install Yarn if missing? (Y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            install_yarn
        fi
        
        read -p "Install MongoDB if missing? (Y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            install_mongodb
        fi
    fi
    
    # Setup backend
    setup_backend
    
    # Setup frontend
    setup_frontend
    
    # Configure environments
    setup_backend_env
    setup_frontend_env
    
    # Create directories
    create_directories
    
    # Print summary
    print_summary
    
    log "Installation completed successfully!"
}

# Run main function
main "$@"
