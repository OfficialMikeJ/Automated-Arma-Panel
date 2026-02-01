#!/bin/bash

###############################################################################
# Tactical Command - Panel Update Script
#
# This script updates the panel with new features, security fixes, and patches
#
# IMPORTANT: Always run with sudo bash
#   sudo bash ./update-panel.sh
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Directories
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
SCRIPTS_DIR="$ROOT_DIR/scripts"

# Log file
LOG_FILE="$ROOT_DIR/update.log"

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
    echo -e "${CYAN}║${NC}        ${GREEN}TACTICAL COMMAND - PANEL UPDATE UTILITY${NC}           ${CYAN}║${NC}"
    echo -e "${CYAN}║                                                                   ║${NC}"
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

###############################################################################
# Main Update Function
###############################################################################

update_panel() {
    print_header
    
    info "Starting Tactical Command panel update..."
    echo ""
    
    # Check if running as root/sudo
    if [ "$EUID" -ne 0 ]; then
        error "This script must be run with sudo"
        echo ""
        echo "Usage: sudo bash ./update-panel.sh"
        echo ""
        exit 1
    fi
    
    # Create backup
    log "Step 1: Creating backup..."
    BACKUP_DIR="$ROOT_DIR/backups/pre-update-$(date +'%Y%m%d_%H%M%S')"
    mkdir -p "$BACKUP_DIR"
    
    # Backup database
    if [ -f "$BACKEND_DIR/.env" ]; then
        source "$BACKEND_DIR/.env"
        if [ ! -z "$MONGO_URL" ] && [ ! -z "$DB_NAME" ]; then
            info "Backing up MongoDB database..."
            mongodump --uri="$MONGO_URL" --db="$DB_NAME" --out="$BACKUP_DIR/database" 2>/dev/null || warn "MongoDB backup failed (mongodump not installed)"
        fi
    fi
    
    # Backup configurations
    info "Backing up configuration files..."
    [ -f "$BACKEND_DIR/.env" ] && cp "$BACKEND_DIR/.env" "$BACKUP_DIR/backend.env"
    [ -f "$FRONTEND_DIR/.env" ] && cp "$FRONTEND_DIR/.env" "$BACKUP_DIR/frontend.env"
    
    success "✓ Backup created at: $BACKUP_DIR"
    echo ""
    
    # Update backend dependencies
    log "Step 2: Updating backend dependencies..."
    cd "$BACKEND_DIR"
    
    if [ -d "venv" ]; then
        source venv/bin/activate
        info "Upgrading pip..."
        pip install --quiet --upgrade pip
        info "Updating Python dependencies..."
        pip install --quiet --upgrade -r requirements.txt
        deactivate
        success "✓ Backend dependencies updated"
    else
        warn "Virtual environment not found, skipping backend update"
    fi
    echo ""
    
    # Update frontend dependencies
    log "Step 3: Updating frontend dependencies..."
    cd "$FRONTEND_DIR"
    
    if [ -d "node_modules" ]; then
        info "Updating Node.js dependencies..."
        yarn upgrade --silent 2>/dev/null || npm update --silent
        success "✓ Frontend dependencies updated"
    else
        warn "node_modules not found, skipping frontend update"
    fi
    echo ""
    
    # Run database migrations (if any)
    log "Step 4: Checking for database migrations..."
    if [ -f "$BACKEND_DIR/migrations.py" ]; then
        cd "$BACKEND_DIR"
        source venv/bin/activate
        python migrations.py
        deactivate
        success "✓ Database migrations applied"
    else
        info "No database migrations needed"
    fi
    echo ""
    
    # Restart services
    log "Step 5: Restarting services..."
    info "Restarting backend and frontend..."
    
    sudo supervisorctl restart backend frontend 2>/dev/null || warn "Could not restart services via supervisor (may need manual restart)"
    
    success "✓ Services restarted"
    echo ""
    
    # Verify update
    log "Step 6: Verifying update..."
    sleep 3
    
    # Check backend
    BACKEND_STATUS=$(sudo supervisorctl status backend 2>/dev/null | grep RUNNING || echo "UNKNOWN")
    if [[ $BACKEND_STATUS == *"RUNNING"* ]]; then
        success "✓ Backend is running"
    else
        warn "Backend status: $BACKEND_STATUS"
    fi
    
    # Check frontend
    FRONTEND_STATUS=$(sudo supervisorctl status frontend 2>/dev/null | grep RUNNING || echo "UNKNOWN")
    if [[ $FRONTEND_STATUS == *"RUNNING"* ]]; then
        success "✓ Frontend is running"
    else
        warn "Frontend status: $FRONTEND_STATUS"
    fi
    
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  UPDATE COMPLETE!${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    info "Backup location: $BACKUP_DIR"
    info "Update log: $LOG_FILE"
    echo ""
    info "Access your panel:"
    echo "  • Frontend: http://localhost:3000"
    echo "  • Backend API: http://localhost:8001"
    echo ""
}

###############################################################################
# Rollback Function
###############################################################################

rollback_update() {
    print_header
    echo ""
    warn "Rolling back to previous version..."
    echo ""
    
    # List available backups
    if [ -d "$ROOT_DIR/backups" ]; then
        echo "Available backups:"
        ls -lt "$ROOT_DIR/backups" | grep "^d" | head -5
        echo ""
        read -p "Enter backup directory name to restore: " BACKUP_NAME
        
        RESTORE_DIR="$ROOT_DIR/backups/$BACKUP_NAME"
        
        if [ -d "$RESTORE_DIR" ]; then
            info "Restoring from $RESTORE_DIR..."
            
            # Restore configurations
            [ -f "$RESTORE_DIR/backend.env" ] && cp "$RESTORE_DIR/backend.env" "$BACKEND_DIR/.env"
            [ -f "$RESTORE_DIR/frontend.env" ] && cp "$RESTORE_DIR/frontend.env" "$FRONTEND_DIR/.env"
            
            # Restore database
            if [ -d "$RESTORE_DIR/database" ]; then
                info "Restoring MongoDB database..."
                source "$BACKEND_DIR/.env"
                mongorestore --uri="$MONGO_URL" --db="$DB_NAME" "$RESTORE_DIR/database/$DB_NAME" --drop 2>/dev/null || warn "Database restore failed"
            fi
            
            success "✓ Rollback complete"
            info "Please restart services manually if needed"
        else
            error "Backup directory not found: $RESTORE_DIR"
        fi
    else
        error "No backups found"
    fi
    echo ""
}

###############################################################################
# Main Menu
###############################################################################

show_menu() {
    print_header
    
    echo "Select an option:"
    echo ""
    echo "  1) Update Panel (Recommended)"
    echo "  2) Rollback to Previous Version"
    echo "  3) View Update Log"
    echo "  4) Exit"
    echo ""
    read -p "Enter choice [1-4]: " choice
    
    case $choice in
        1)
            update_panel
            ;;
        2)
            rollback_update
            ;;
        3)
            if [ -f "$LOG_FILE" ]; then
                less "$LOG_FILE"
            else
                error "No update log found"
            fi
            ;;
        4)
            info "Exiting..."
            exit 0
            ;;
        *)
            error "Invalid choice"
            sleep 2
            show_menu
            ;;
    esac
}

###############################################################################
# Entry Point
###############################################################################

# Parse arguments
case "${1:-}" in
    --auto)
        update_panel
        ;;
    --rollback)
        rollback_update
        ;;
    *)
        show_menu
        ;;
esac
