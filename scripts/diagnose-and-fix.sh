#!/bin/bash

###############################################################################
# Tactical Command - Installation Diagnostic & Repair Tool
#
# This script checks the installation and attempts to fix common issues
#
# Usage: sudo bash ./diagnose-and-fix.sh
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Directories
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

log() {
    echo -e "${GREEN}[CHECK]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_header() {
    clear
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  Tactical Command - Diagnostic & Repair Tool${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
}

###############################################################################
# Diagnostic Functions
###############################################################################

check_python() {
    log "Checking Python installation..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d" " -f2)
        success "Python $PYTHON_VERSION installed"
        return 0
    else
        error "Python 3 not installed"
        return 1
    fi
}

check_python_venv() {
    log "Checking python3-venv package..."
    if dpkg -l 2>/dev/null | grep -q "python3.*-venv"; then
        success "python3-venv installed"
        return 0
    else
        error "python3-venv not installed"
        return 1
    fi
}

check_nodejs() {
    log "Checking Node.js installation..."
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        NODE_MAJOR=$(echo $NODE_VERSION | cut -d'v' -f2 | cut -d'.' -f1)
        
        if [ "$NODE_MAJOR" -ge 20 ]; then
            success "Node.js $NODE_VERSION (compatible)"
            return 0
        else
            warn "Node.js $NODE_VERSION (needs upgrade to 20.x)"
            return 2
        fi
    else
        error "Node.js not installed"
        return 1
    fi
}

check_mongodb() {
    log "Checking MongoDB..."
    if command -v mongod &> /dev/null; then
        if systemctl is-active --quiet mongod || systemctl is-active --quiet mongodb; then
            success "MongoDB installed and running"
            return 0
        else
            warn "MongoDB installed but not running"
            return 2
        fi
    else
        error "MongoDB not installed"
        return 1
    fi
}

check_backend_venv() {
    log "Checking backend virtual environment..."
    if [ -d "$BACKEND_DIR/venv" ]; then
        if [ -f "$BACKEND_DIR/venv/bin/activate" ]; then
            success "Backend venv exists"
            return 0
        else
            error "Backend venv corrupted"
            return 2
        fi
    else
        error "Backend venv not found"
        return 1
    fi
}

check_backend_uvicorn() {
    log "Checking uvicorn installation..."
    if [ -f "$BACKEND_DIR/venv/bin/uvicorn" ]; then
        success "uvicorn installed in venv"
        return 0
    else
        error "uvicorn not found"
        return 1
    fi
}

check_frontend_deps() {
    log "Checking frontend dependencies..."
    if [ -d "$FRONTEND_DIR/node_modules" ]; then
        if [ -d "$FRONTEND_DIR/node_modules/react" ] && [ -d "$FRONTEND_DIR/node_modules/react-router-dom" ]; then
            success "Frontend dependencies installed"
            return 0
        else
            warn "Frontend dependencies incomplete"
            return 2
        fi
    else
        error "node_modules not found"
        return 1
    fi
}

check_services() {
    log "Checking systemd services..."
    
    local backend_status=0
    local frontend_status=0
    
    if systemctl is-active --quiet tactical-backend; then
        success "Backend service running"
    else
        warn "Backend service not running"
        backend_status=1
    fi
    
    if systemctl is-active --quiet tactical-frontend; then
        success "Frontend service running"
    else
        warn "Frontend service not running"
        frontend_status=1
    fi
    
    if [ $backend_status -eq 1 ] || [ $frontend_status -eq 1 ]; then
        return 2
    fi
    
    return 0
}

###############################################################################
# Repair Functions
###############################################################################

fix_python_venv_package() {
    echo ""
    info "Installing python3-venv package..."
    sudo apt-get update
    sudo apt-get install -y python3-venv
    success "python3-venv installed"
}

fix_nodejs_upgrade() {
    echo ""
    info "Upgrading Node.js to 20.x..."
    sudo apt-get remove -y nodejs
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
    success "Node.js upgraded to $(node --version)"
}

fix_mongodb_start() {
    echo ""
    info "Starting MongoDB..."
    sudo systemctl start mongod || sudo systemctl start mongodb
    sudo systemctl enable mongod || sudo systemctl enable mongodb
    success "MongoDB started"
}

fix_backend_venv() {
    echo ""
    info "Creating backend virtual environment..."
    cd "$BACKEND_DIR"
    rm -rf venv
    python3 -m venv venv
    success "Backend venv created"
}

fix_backend_dependencies() {
    echo ""
    info "Installing backend dependencies..."
    cd "$BACKEND_DIR"
    
    # Handle emergentintegrations
    if grep -q "emergentintegrations" requirements.txt; then
        warn "emergentintegrations found in requirements.txt"
        read -p "Remove emergentintegrations from requirements? (Y/n): " -r
        echo ""
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            grep -v "emergentintegrations" requirements.txt > requirements_temp.txt
            mv requirements_temp.txt requirements.txt
            info "emergentintegrations removed"
        fi
    fi
    
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    deactivate
    
    success "Backend dependencies installed"
}

fix_frontend_dependencies() {
    echo ""
    info "Installing frontend dependencies..."
    cd "$FRONTEND_DIR"
    rm -rf node_modules
    yarn install
    success "Frontend dependencies installed"
}

fix_services() {
    echo ""
    info "Restarting services..."
    sudo systemctl daemon-reload
    sudo systemctl restart tactical-backend tactical-frontend
    sleep 3
    success "Services restarted"
}

###############################################################################
# Main Diagnostic Flow
###############################################################################

main() {
    print_header
    
    local issues_found=0
    local fixes_needed=()
    
    # Run all checks
    echo "Running diagnostics..."
    echo ""
    
    check_python || { issues_found=$((issues_found + 1)); }
    
    check_python_venv || { issues_found=$((issues_found + 1)); fixes_needed+=("python_venv"); }
    
    nodejs_result=0
    check_nodejs || nodejs_result=$?
    if [ $nodejs_result -eq 1 ]; then
        issues_found=$((issues_found + 1))
    elif [ $nodejs_result -eq 2 ]; then
        issues_found=$((issues_found + 1))
        fixes_needed+=("nodejs_upgrade")
    fi
    
    mongodb_result=0
    check_mongodb || mongodb_result=$?
    if [ $mongodb_result -eq 1 ]; then
        issues_found=$((issues_found + 1))
    elif [ $mongodb_result -eq 2 ]; then
        fixes_needed+=("mongodb_start")
    fi
    
    backend_venv_result=0
    check_backend_venv || backend_venv_result=$?
    if [ $backend_venv_result -ne 0 ]; then
        issues_found=$((issues_found + 1))
        fixes_needed+=("backend_venv")
    fi
    
    check_backend_uvicorn || { issues_found=$((issues_found + 1)); fixes_needed+=("backend_deps"); }
    
    frontend_result=0
    check_frontend_deps || frontend_result=$?
    if [ $frontend_result -ne 0 ]; then
        issues_found=$((issues_found + 1))
        fixes_needed+=("frontend_deps")
    fi
    
    check_services || fixes_needed+=("services")
    
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    
    if [ $issues_found -eq 0 ] && [ ${#fixes_needed[@]} -eq 0 ]; then
        success "✓ No issues found! Installation is healthy."
        echo ""
        exit 0
    fi
    
    echo ""
    warn "Found $issues_found issue(s) that need attention"
    echo ""
    
    # Offer to fix issues
    if [ ${#fixes_needed[@]} -gt 0 ]; then
        echo "The following fixes can be applied:"
        for fix in "${fixes_needed[@]}"; do
            case $fix in
                python_venv) echo "  • Install python3-venv package" ;;
                nodejs_upgrade) echo "  • Upgrade Node.js to 20.x" ;;
                mongodb_start) echo "  • Start MongoDB service" ;;
                backend_venv) echo "  • Recreate backend virtual environment" ;;
                backend_deps) echo "  • Install backend dependencies" ;;
                frontend_deps) echo "  • Install frontend dependencies" ;;
                services) echo "  • Restart services" ;;
            esac
        done
        echo ""
        
        read -p "Would you like to apply these fixes automatically? (Y/n): " -r
        echo ""
        
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            for fix in "${fixes_needed[@]}"; do
                case $fix in
                    python_venv) fix_python_venv_package ;;
                    nodejs_upgrade) fix_nodejs_upgrade ;;
                    mongodb_start) fix_mongodb_start ;;
                    backend_venv) fix_backend_venv ;;
                    backend_deps) fix_backend_dependencies ;;
                    frontend_deps) fix_frontend_dependencies ;;
                    services) fix_services ;;
                esac
            done
            
            echo ""
            success "✓ All fixes applied!"
            echo ""
            info "Verifying installation..."
            echo ""
            
            # Re-run checks
            $0
        else
            echo ""
            info "No fixes applied. Please fix issues manually."
            echo ""
        fi
    else
        info "Please fix the issues manually and re-run this diagnostic."
        echo ""
    fi
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    error "This script must be run with sudo"
    echo ""
    echo "Usage: sudo bash ./diagnose-and-fix.sh"
    echo ""
    exit 1
fi

main "$@"
