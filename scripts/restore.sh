#!/bin/bash

###############################################################################
# Tactical Command - Restore Script
#
# This script restores a backup created by backup.sh including:
# - MongoDB database
# - Server configurations
# - Server logs
# - Environment files
#
# Usage:
#   ./restore.sh <backup-name>
#
# Example:
#   ./restore.sh backup_20240127_153045
#   ./restore.sh my-backup
###############################################################################

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Directories
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)"
BACKUP_DIR="$ROOT_DIR/backups"
BACKUP_NAME="$1"
RESTORE_TEMP="$BACKUP_DIR/restore_temp"

# Log functions
log() {
    echo -e "${GREEN}[RESTORE]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_header() {
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "  Tactical Command - Restore Script"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
}

show_usage() {
    cat << EOF
Usage: $0 <backup-name>

Restore a backup created by backup.sh

Examples:
    $0 backup_20240127_153045
    $0 my-backup

Available backups:
EOF
    if [ -d "$BACKUP_DIR" ]; then
        ls -1 "$BACKUP_DIR"/*.tar.gz 2>/dev/null | xargs -n1 basename | sed 's/.tar.gz$//' | sed 's/^/    /'
    else
        echo "    No backups found"
    fi
    echo ""
}

check_backup_exists() {
    if [ -z "$BACKUP_NAME" ]; then
        error "No backup name provided"
        show_usage
        exit 1
    fi
    
    BACKUP_FILE="$BACKUP_DIR/${BACKUP_NAME}.tar.gz"
    
    if [ ! -f "$BACKUP_FILE" ]; then
        error "Backup file not found: $BACKUP_FILE"
        show_usage
        exit 1
    fi
    
    log "Found backup: $BACKUP_FILE"
}

check_dependencies() {
    log "Checking dependencies..."
    
    if ! command -v mongorestore &> /dev/null; then
        error "mongorestore is not installed. Please install mongodb-database-tools."
        exit 1
    fi
    
    log "✓ All dependencies available"
}

confirm_restore() {
    warn "This will restore the backup and may overwrite existing data!"
    info "Backup: $BACKUP_NAME"
    info "File: $BACKUP_FILE"
    echo ""
    read -p "Are you sure you want to continue? (yes/no): " -r CONFIRM
    
    if [ "$CONFIRM" != "yes" ]; then
        log "Restore cancelled"
        exit 0
    fi
    
    echo ""
}

extract_backup() {
    log "Extracting backup..."
    
    # Create temp directory
    mkdir -p "$RESTORE_TEMP"
    
    # Extract backup
    tar -xzf "$BACKUP_FILE" -C "$RESTORE_TEMP"
    
    BACKUP_PATH="$RESTORE_TEMP/$BACKUP_NAME"
    
    if [ ! -d "$BACKUP_PATH" ]; then
        error "Backup extraction failed"
        exit 1
    fi
    
    log "✓ Backup extracted"
}

show_backup_info() {
    if [ -f "$BACKUP_PATH/backup_info.txt" ]; then
        echo ""
        cat "$BACKUP_PATH/backup_info.txt"
        echo ""
    fi
}

stop_services() {
    log "Stopping services..."
    
    # Check if systemd services are running
    if systemctl is-active --quiet tactical-backend; then
        sudo systemctl stop tactical-backend
        log "✓ Stopped backend service"
    fi
    
    if systemctl is-active --quiet tactical-frontend; then
        sudo systemctl stop tactical-frontend
        log "✓ Stopped frontend service"
    fi
    
    # Give services time to stop
    sleep 2
}

restore_database() {
    log "Restoring MongoDB database..."
    
    # Get MongoDB URL from backup or use default
    if [ -f "$BACKUP_PATH/env/backend.env" ]; then
        MONGO_URL=$(grep MONGO_URL "$BACKUP_PATH/env/backend.env" | cut -d '=' -f2 | tr -d '"')
        DB_NAME=$(grep DB_NAME "$BACKUP_PATH/env/backend.env" | cut -d '=' -f2 | tr -d '"')
    else
        MONGO_URL="mongodb://localhost:27017"
        DB_NAME="arma_server_panel"
    fi
    
    # Drop existing database
    warn "Dropping existing database: $DB_NAME"
    mongosh "$MONGO_URL/$DB_NAME" --quiet --eval "db.dropDatabase()" 2>/dev/null || true
    
    # Restore database
    mongorestore --uri="$MONGO_URL" --db="$DB_NAME" "$BACKUP_PATH/database/$DB_NAME" --quiet
    
    if [ $? -eq 0 ]; then
        log "✓ Database restored"
    else
        error "Database restore failed"
        exit 1
    fi
}

restore_configs() {
    log "Restoring server configurations..."
    
    if [ -d "$BACKUP_PATH/configs/tmp/arma_servers" ]; then
        # Create base directory
        mkdir -p /tmp/arma_servers
        
        # Copy configs back
        cp -r "$BACKUP_PATH/configs/tmp/arma_servers"/* /tmp/arma_servers/ 2>/dev/null || true
        
        CONFIG_COUNT=$(find /tmp/arma_servers -name "server.cfg" | wc -l)
        log "✓ Restored $CONFIG_COUNT server configuration(s)"
    else
        warn "No server configurations in backup"
    fi
}

restore_logs() {
    log "Restoring server logs..."
    
    if [ -d "$BACKUP_PATH/logs/tmp/arma_servers" ]; then
        # Create base directory
        mkdir -p /tmp/arma_servers
        
        # Copy logs back
        cp -r "$BACKUP_PATH/logs/tmp/arma_servers"/* /tmp/arma_servers/ 2>/dev/null || true
        
        LOG_COUNT=$(find /tmp/arma_servers -name "*.log" | wc -l)
        log "✓ Restored $LOG_COUNT log file(s)"
    else
        warn "No server logs in backup"
    fi
}

restore_environment() {
    log "Restoring environment files..."
    
    # Restore backend .env
    if [ -f "$BACKUP_PATH/env/backend.env" ]; then
        cp "$BACKUP_PATH/env/backend.env" "$ROOT_DIR/backend/.env"
        log "✓ Backend .env restored"
    fi
    
    # Restore frontend .env
    if [ -f "$BACKUP_PATH/env/frontend.env" ]; then
        cp "$BACKUP_PATH/env/frontend.env" "$ROOT_DIR/frontend/.env"
        log "✓ Frontend .env restored"
    fi
}

start_services() {
    log "Starting services..."
    
    # Check if systemd services exist
    if [ -f "/etc/systemd/system/tactical-backend.service" ]; then
        sudo systemctl start tactical-backend
        log "✓ Started backend service"
    else
        info "Backend service not configured. Start manually if needed."
    fi
    
    if [ -f "/etc/systemd/system/tactical-frontend.service" ]; then
        sudo systemctl start tactical-frontend
        log "✓ Started frontend service"
    else
        info "Frontend service not configured. Start manually if needed."
    fi
}

cleanup() {
    log "Cleaning up temporary files..."
    rm -rf "$RESTORE_TEMP"
    log "✓ Cleanup complete"
}

print_summary() {
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo -e "  ${GREEN}Restore Complete!${NC}"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "Restored from: $BACKUP_NAME"
    echo ""
    echo "Next steps:"
    echo "  1. Verify services are running:"
    echo "     sudo systemctl status tactical-backend"
    echo "     sudo systemctl status tactical-frontend"
    echo ""
    echo "  2. Access the panel and verify data"
    echo ""
    echo "  3. Check server logs if needed:"
    echo "     journalctl -u tactical-backend -n 50"
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo ""
}

main() {
    print_header
    
    check_backup_exists
    check_dependencies
    show_backup_info
    confirm_restore
    
    log "Starting restore from: $BACKUP_NAME"
    
    extract_backup
    stop_services
    restore_database
    restore_configs
    restore_logs
    restore_environment
    start_services
    cleanup
    
    print_summary
    
    log "Restore completed successfully!"
}

# Run main
main "$@"