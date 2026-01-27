#!/bin/bash

###############################################################################
# Tactical Command - Backup Script
#
# This script creates a complete backup of the panel including:
# - MongoDB database
# - Server configurations
# - Server logs
# - Environment files
#
# Usage:
#   ./backup.sh [backup-name]
#
# Example:
#   ./backup.sh my-backup
#   ./backup.sh  # Uses timestamp as name
###############################################################################

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Directories
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)"
BACKUP_DIR="$ROOT_DIR/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="${1:-backup_$TIMESTAMP}"
BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"

# Log functions
log() {
    echo -e "${GREEN}[BACKUP]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_header() {
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "  Tactical Command - Backup Script"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
}

check_dependencies() {
    log "Checking dependencies..."
    
    if ! command -v mongodump &> /dev/null; then
        error "mongodump is not installed. Please install mongodb-database-tools."
        exit 1
    fi
    
    log "✓ All dependencies available"
}

create_backup_structure() {
    log "Creating backup directory structure..."
    
    mkdir -p "$BACKUP_PATH"
    mkdir -p "$BACKUP_PATH/database"
    mkdir -p "$BACKUP_PATH/configs"
    mkdir -p "$BACKUP_PATH/logs"
    mkdir -p "$BACKUP_PATH/env"
    
    log "✓ Backup directory created: $BACKUP_PATH"
}

backup_database() {
    log "Backing up MongoDB database..."
    
    # Get MongoDB URL from backend .env
    if [ -f "$ROOT_DIR/backend/.env" ]; then
        MONGO_URL=$(grep MONGO_URL "$ROOT_DIR/backend/.env" | cut -d '=' -f2 | tr -d '"')
        DB_NAME=$(grep DB_NAME "$ROOT_DIR/backend/.env" | cut -d '=' -f2 | tr -d '"')
    else
        MONGO_URL="mongodb://localhost:27017"
        DB_NAME="arma_server_panel"
    fi
    
    # Dump database
    mongodump --uri="$MONGO_URL" --db="$DB_NAME" --out="$BACKUP_PATH/database" --quiet
    
    if [ $? -eq 0 ]; then
        log "✓ Database backup completed"
        # Get collection counts
        USERS_COUNT=$(find "$BACKUP_PATH/database/$DB_NAME" -name "users.bson" -exec stat -f%z {} \; 2>/dev/null || echo "0")
        SERVERS_COUNT=$(find "$BACKUP_PATH/database/$DB_NAME" -name "servers.bson" -exec stat -f%z {} \; 2>/dev/null || echo "0")
        log "  - Database: $DB_NAME"
    else
        error "Database backup failed"
        exit 1
    fi
}

backup_configs() {
    log "Backing up server configurations..."
    
    if [ -d "/tmp/arma_servers" ]; then
        # Copy all server configs
        find /tmp/arma_servers -name "server.cfg" -exec cp --parents {} "$BACKUP_PATH/configs" \; 2>/dev/null || true
        CONFIG_COUNT=$(find "$BACKUP_PATH/configs" -name "server.cfg" | wc -l)
        log "✓ Backed up $CONFIG_COUNT server configuration(s)"
    else
        warn "No server configurations found"
    fi
}

backup_logs() {
    log "Backing up server logs..."
    
    if [ -d "/tmp/arma_servers" ]; then
        # Copy recent logs (last 7 days)
        find /tmp/arma_servers -name "*.log" -mtime -7 -exec cp --parents {} "$BACKUP_PATH/logs" \; 2>/dev/null || true
        LOG_COUNT=$(find "$BACKUP_PATH/logs" -name "*.log" | wc -l)
        log "✓ Backed up $LOG_COUNT log file(s) (last 7 days)"
    else
        warn "No server logs found"
    fi
}

backup_environment() {
    log "Backing up environment files..."
    
    # Backup backend .env
    if [ -f "$ROOT_DIR/backend/.env" ]; then
        cp "$ROOT_DIR/backend/.env" "$BACKUP_PATH/env/backend.env"
        log "✓ Backend .env backed up"
    fi
    
    # Backup frontend .env
    if [ -f "$ROOT_DIR/frontend/.env" ]; then
        cp "$ROOT_DIR/frontend/.env" "$BACKUP_PATH/env/frontend.env"
        log "✓ Frontend .env backed up"
    fi
}

create_metadata() {
    log "Creating backup metadata..."
    
    cat > "$BACKUP_PATH/backup_info.txt" << EOF
Tactical Command - Backup Information
=====================================

Backup Name: $BACKUP_NAME
Backup Date: $(date)
Hostname: $(hostname)
Backup Path: $BACKUP_PATH

Contents:
---------
- MongoDB Database: $DB_NAME
- Server Configurations: $(find "$BACKUP_PATH/configs" -name "server.cfg" | wc -l)
- Server Logs: $(find "$BACKUP_PATH/logs" -name "*.log" | wc -l)
- Environment Files: 2

Restore Command:
----------------
cd $ROOT_DIR/scripts
./restore.sh $BACKUP_NAME

EOF
    
    log "✓ Metadata created"
}

compress_backup() {
    log "Compressing backup..."
    
    cd "$BACKUP_DIR"
    tar -czf "${BACKUP_NAME}.tar.gz" "$BACKUP_NAME" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        BACKUP_SIZE=$(du -h "${BACKUP_NAME}.tar.gz" | cut -f1)
        log "✓ Backup compressed: ${BACKUP_NAME}.tar.gz ($BACKUP_SIZE)"
        
        # Remove uncompressed directory
        rm -rf "$BACKUP_NAME"
    else
        error "Compression failed"
        exit 1
    fi
}

cleanup_old_backups() {
    log "Cleaning up old backups (keeping last 10)..."
    
    cd "$BACKUP_DIR"
    BACKUP_COUNT=$(ls -1 *.tar.gz 2>/dev/null | wc -l)
    
    if [ $BACKUP_COUNT -gt 10 ]; then
        ls -1t *.tar.gz | tail -n +11 | xargs rm -f
        REMOVED=$((BACKUP_COUNT - 10))
        log "✓ Removed $REMOVED old backup(s)"
    else
        log "✓ No old backups to remove ($BACKUP_COUNT total)"
    fi
}

print_summary() {
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo -e "  ${GREEN}Backup Complete!${NC}"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "Backup File: $BACKUP_DIR/${BACKUP_NAME}.tar.gz"
    echo "Backup Size: $(du -h "$BACKUP_DIR/${BACKUP_NAME}.tar.gz" | cut -f1)"
    echo ""
    echo "To restore this backup:"
    echo "  cd $ROOT_DIR/scripts"
    echo "  ./restore.sh $BACKUP_NAME"
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo ""
}

main() {
    print_header
    
    log "Starting backup: $BACKUP_NAME"
    log "Backup location: $BACKUP_PATH"
    
    check_dependencies
    create_backup_structure
    backup_database
    backup_configs
    backup_logs
    backup_environment
    create_metadata
    compress_backup
    cleanup_old_backups
    
    print_summary
    
    log "Backup completed successfully!"
}

# Run main
main "$@"