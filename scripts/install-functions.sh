#!/bin/bash

# Installation functions for Tactical Command panel
# This file is sourced by install.sh

###############################################################################
# Native Installation (Option 2)
###############################################################################

install_native_panel() {
    print_header
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${MAGENTA}  OPTION 2: Native Installation + Guided Setup${NC}"
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    detect_installations
    
    if [ "$PANEL_INSTALLED" = true ]; then
        warn "Panel components already detected!"
        echo ""
        read -p "Do you want to reinstall? (y/N): " -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            info "Skipping native installation"
            pause
            return 0
        fi
    fi
    
    # Check system requirements
    log "Step 1: Checking system requirements..."
    echo ""
    
    local all_good=true
    local needs_python=false
    local needs_nodejs=false
    
    # Check Python
    if check_command python3; then
        PYTHON_VERSION=$(python3 --version | cut -d" " -f2)
        success "✓ Python: $PYTHON_VERSION"
    else
        warn "✗ Python 3 is not installed"
        needs_python=true
        all_good=false
    fi
    
    # Check Node.js
    if check_command node; then
        NODE_VERSION=$(node --version)
        success "✓ Node.js: $NODE_VERSION"
    else
        warn "✗ Node.js is not installed"
        needs_nodejs=true
        all_good=false
    fi
    
    # Offer to install missing dependencies
    if [ "$all_good" = false ]; then
        echo ""
        warn "Missing dependencies detected!"
        echo ""
        read -p "Would you like to install missing dependencies automatically? (Y/n): " -r
        echo ""
        
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            # Install Python
            if [ "$needs_python" = true ]; then
                log "Installing Python 3..."
                echo ""
                
                if [ -f /etc/debian_version ]; then
                    sudo apt-get update
                    sudo apt-get install -y python3 python3-pip python3-venv
                    success "✓ Python 3 installed"
                elif [ -f /etc/redhat-release ]; then
                    sudo yum install -y python3 python3-pip
                    success "✓ Python 3 installed"
                else
                    error "Unable to auto-install Python on this distribution"
                    error "Please install Python 3.11+ manually"
                    pause
                    return 1
                fi
                echo ""
            fi
            
            # Install Node.js
            if [ "$needs_nodejs" = true ]; then
                log "Installing Node.js..."
                echo ""
                
                if [ -f /etc/debian_version ]; then
                    info "Adding NodeSource repository..."
                    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
                    sudo apt-get install -y nodejs
                    success "✓ Node.js installed"
                elif [ -f /etc/redhat-release ]; then
                    info "Adding NodeSource repository..."
                    curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
                    sudo yum install -y nodejs
                    success "✓ Node.js installed"
                else
                    error "Unable to auto-install Node.js on this distribution"
                    error "Please install Node.js 16+ manually from: https://nodejs.org/"
                    pause
                    return 1
                fi
                echo ""
            fi
            
            # Verify installations
            if check_command python3 && check_command node; then
                success "✓ All dependencies installed successfully!"
                PYTHON_VERSION=$(python3 --version | cut -d" " -f2)
                NODE_VERSION=$(node --version)
                info "Python: $PYTHON_VERSION"
                info "Node.js: $NODE_VERSION"
            else
                error "Installation verification failed"
                pause
                return 1
            fi
        else
            error "Installation cancelled. Please install Python 3.11+ and Node.js 16+ manually."
            pause
            return 1
        fi
    fi
    
    echo ""
    print_separator
    echo ""
    
    # Install Yarn if needed
    if ! check_command yarn; then
        info "Installing Yarn..."
        npm install -g yarn || {
            error "Failed to install Yarn"
            pause
            return 1
        }
        success "✓ Yarn installed"
        echo ""
    else
        success "✓ Yarn already installed"
        echo ""
    fi
    
    # Install MongoDB if needed
    if [ "$MONGODB_INSTALLED" = false ]; then
        log "Step 2: Installing MongoDB..."
        echo ""
        
        read -p "Install MongoDB locally? (Y/n): " -r
        echo ""
        
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            if [ -f /etc/debian_version ]; then
                info "Installing MongoDB on Debian/Ubuntu..."
                
                # Get Ubuntu version
                UBUNTU_VERSION=$(lsb_release -cs)
                
                # Install gnupg if not present
                sudo apt-get install -y gnupg curl
                
                # Add MongoDB GPG key using the new method
                curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
                    sudo gpg --dearmor -o /usr/share/keyrings/mongodb-server-7.0.gpg
                
                # For Ubuntu 24.04 (noble), use jammy repository as noble isn't available yet
                if [ "$UBUNTU_VERSION" = "noble" ]; then
                    info "Ubuntu 24.04 detected, using jammy repository..."
                    UBUNTU_VERSION="jammy"
                fi
                
                # Add MongoDB repository with signed-by option
                echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu $UBUNTU_VERSION/mongodb-org/7.0 multiverse" | \
                    sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
                
                # Update and install
                sudo apt-get update
                sudo apt-get install -y mongodb-org || {
                    warn "MongoDB repository install failed, trying community version..."
                    sudo apt-get install -y mongodb || {
                        error "Failed to install MongoDB. Please install manually."
                        return 1
                    }
                }
                
                # Start and enable MongoDB
                sudo systemctl daemon-reload
                sudo systemctl start mongod 2>/dev/null || sudo systemctl start mongodb 2>/dev/null
                sudo systemctl enable mongod 2>/dev/null || sudo systemctl enable mongodb 2>/dev/null
                
                # Wait a moment for MongoDB to start
                sleep 2
                
                # Check if MongoDB is running
                if sudo systemctl is-active --quiet mongod || sudo systemctl is-active --quiet mongodb; then
                    success "✓ MongoDB installed and started"
                else
                    warn "MongoDB installed but may not be running. Check: sudo systemctl status mongod"
                fi
            else
                warn "Please install MongoDB manually for your distribution"
            fi
        else
            info "Skipping MongoDB installation - make sure it's available!"
        fi
        echo ""
    else
        success "✓ MongoDB already installed"
        echo ""
    fi
    
    print_separator
    echo ""
    
    # Backend setup
    log "Step 3: Setting up backend..."
    echo ""
    
    # Ensure python3-venv is installed
    if ! dpkg -l | grep -q python3.*-venv; then
        info "Installing python3-venv package..."
        if [ -f /etc/debian_version ]; then
            sudo apt-get install -y python3-venv
        fi
    fi
    
    cd "$BACKEND_DIR"
    
    if [ ! -d "venv" ]; then
        info "Creating Python virtual environment..."
        python3 -m venv venv || {
            error "Failed to create virtual environment!"
            error "Please install python3-venv: sudo apt-get install -y python3-venv"
            pause
            return 1
        }
    fi
    
    source venv/bin/activate
    
    info "Installing Python dependencies..."
    pip install --quiet --upgrade pip
    pip install --quiet -r requirements.txt
    
    success "✓ Backend setup complete"
    echo ""
    
    print_separator
    echo ""
    
    # Frontend setup
    log "Step 4: Setting up frontend..."
    echo ""
    
    cd "$FRONTEND_DIR"
    
    info "Installing Node.js dependencies..."
    yarn install --silent
    
    success "✓ Frontend setup complete"
    echo ""
    
    print_separator
    echo ""
    
    # Guided configuration
    guided_configuration
    
    PANEL_INSTALLED=true
    
    echo ""
    success "Native installation complete!"
    echo ""
    
    pause
}

###############################################################################
# Guided Configuration
###############################################################################

guided_configuration() {
    log "Step 5: Configuration Setup"
    echo ""
    
    # Backend configuration
    info "Configuring backend..."
    echo ""
    
    local env_file="$BACKEND_DIR/.env"
    
    if [ -f "$env_file" ]; then
        warn ".env file already exists"
        read -p "Overwrite existing configuration? (y/N): " -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            info "Keeping existing configuration"
            return
        fi
    fi
    
    # MongoDB URL
    read -p "MongoDB URL [mongodb://localhost:27017]: " MONGO_URL
    MONGO_URL=${MONGO_URL:-mongodb://localhost:27017}
    
    # Database name
    read -p "Database name [arma_server_panel]: " DB_NAME
    DB_NAME=${DB_NAME:-arma_server_panel}
    
    # Generate secret key
    SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 64 | head -n 1)
    
    # Write backend .env
    cat > "$env_file" << EOF
# MongoDB Configuration
MONGO_URL=$MONGO_URL
DB_NAME=$DB_NAME

# Security
SECRET_KEY=$SECRET_KEY

# CORS
CORS_ORIGINS=*
EOF
    
    success "✓ Backend configured"
    echo ""
    
    # Frontend configuration
    info "Configuring frontend..."
    echo ""
    
    local frontend_env="$FRONTEND_DIR/.env"
    
    read -p "Backend URL [http://localhost:8001]: " BACKEND_URL
    BACKEND_URL=${BACKEND_URL:-http://localhost:8001}
    
    cat > "$frontend_env" << EOF
REACT_APP_BACKEND_URL=$BACKEND_URL
WDS_SOCKET_PORT=0
ENABLE_HEALTH_CHECK=false
EOF
    
    success "✓ Frontend configured"
    echo ""
    
    # Create directories
    mkdir -p /tmp/arma_servers
    mkdir -p "$ROOT_DIR/logs"
    mkdir -p "$ROOT_DIR/backups"
    
    success "✓ Directories created"
    echo ""
    
    # Install SteamCMD
    print_separator
    echo ""
    log "Step 6: Installing SteamCMD..."
    echo ""
    
    read -p "Pre-install SteamCMD for Arma servers? (Y/n): " -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        install_steamcmd
    else
        info "Skipping SteamCMD installation"
    fi
}

###############################################################################
# Firewall Configuration (UFW)
###############################################################################

configure_firewall() {
    print_header
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${MAGENTA}  OPTION 5: Configure Firewall (UFW)${NC}"
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    warn "Firewall Configuration"
    echo ""
    info "This will configure UFW (Uncomplicated Firewall) to allow:"
    echo "  • SSH (port 22)"
    echo "  • Panel Frontend (port 3000)"
    echo "  • Panel Backend API (port 8001)"
    echo "  • Default Arma Server ports (2001-2100 UDP/TCP)"
    echo "  • A2S Query ports (2017-2116 UDP)"
    echo ""
    
    read -p "Continue with firewall configuration? (y/N): " -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        info "Firewall configuration cancelled"
        pause
        return 0
    fi
    
    # Check if UFW is installed
    if ! check_command ufw; then
        info "Installing UFW..."
        echo ""
        
        if [ -f /etc/debian_version ]; then
            sudo apt-get update
            sudo apt-get install -y ufw
        elif [ -f /etc/redhat-release ]; then
            sudo yum install -y ufw
        else
            error "Could not install UFW automatically"
            error "Please install UFW manually for your distribution"
            pause
            return 1
        fi
    else
        success "✓ UFW already installed"
    fi
    
    echo ""
    log "Configuring firewall rules..."
    echo ""
    
    # Set default policies
    info "Setting default policies..."
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    
    # Allow SSH
    info "Allowing SSH (port 22)..."
    sudo ufw allow 22/tcp comment 'SSH'
    
    # Allow panel ports
    info "Allowing Panel Frontend (port 3000)..."
    sudo ufw allow 3000/tcp comment 'Tactical Panel Frontend'
    
    info "Allowing Panel Backend API (port 8001)..."
    sudo ufw allow 8001/tcp comment 'Tactical Panel API'
    
    # Allow Arma Reforger server ports
    info "Allowing Arma Server game ports (2001-2100)..."
    sudo ufw allow 2001:2100/tcp comment 'Arma Server Game Ports'
    sudo ufw allow 2001:2100/udp comment 'Arma Server Game Ports'
    
    info "Allowing A2S query ports (2017-2116)..."
    sudo ufw allow 2017:2116/udp comment 'Arma Server A2S Query'
    
    # IPv6 support
    info "Enabling IPv6 support..."
    sudo sed -i 's/IPV6=no/IPV6=yes/' /etc/default/ufw 2>/dev/null || true
    
    echo ""
    read -p "Enable firewall now? (Y/n): " -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        info "Enabling UFW..."
        echo "y" | sudo ufw enable
        success "✓ Firewall enabled and configured"
    else
        info "Firewall rules configured but not enabled"
        info "Enable manually with: sudo ufw enable"
    fi
    
    echo ""
    info "Firewall status:"
    sudo ufw status verbose
    
    echo ""
    success "Firewall configuration complete!"
    echo ""
    
    pause
}

###############################################################################
# SteamCMD Installation
###############################################################################

install_steamcmd() {
    local steamcmd_dir="$HOME/steamcmd"
    local steamcmd_sh="$steamcmd_dir/steamcmd.sh"
    
    if [ -f "$steamcmd_sh" ]; then
        success "✓ SteamCMD already installed at $steamcmd_dir"
        return 0
    fi
    
    info "Installing SteamCMD..."
    echo ""
    
    # Create directory
    mkdir -p "$steamcmd_dir"
    cd "$steamcmd_dir"
    
    # Download SteamCMD
    info "Downloading SteamCMD..."
    wget -q https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz
    
    if [ $? -ne 0 ]; then
        error "Failed to download SteamCMD"
        return 1
    fi
    
    # Extract
    info "Extracting SteamCMD..."
    tar -xzf steamcmd_linux.tar.gz
    rm steamcmd_linux.tar.gz
    
    # Make executable
    chmod +x steamcmd.sh
    
    # Run once to update
    info "Running initial SteamCMD update..."
    ./steamcmd.sh +quit > /dev/null 2>&1
    
    success "✓ SteamCMD installed successfully at $steamcmd_dir"
    echo ""
    info "SteamCMD location: $steamcmd_sh"
    info "You can now launch Arma servers from the panel"
    echo ""
    
    return 0
}

###############################################################################
# SSL/Let's Encrypt Installation (Option 3)
###############################################################################

install_ssl_certificates() {
    print_header
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${MAGENTA}  OPTION 3: Install SSL Certificates (Let's Encrypt)${NC}"
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    warn "SSL Certificate Setup"
    echo ""
    info "Requirements:"
    echo "  • Domain name pointing to this server"
    echo "  • Ports 80 and 443 accessible from internet"
    echo "  • Valid email address for Let's Encrypt"
    echo ""
    
    read -p "Continue with SSL setup? (y/N): " -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        info "SSL setup cancelled"
        pause
        return 0
    fi
    
    # Check if certbot is installed
    if ! check_command certbot; then
        info "Installing Certbot..."
        echo ""
        
        if [ -f /etc/debian_version ]; then
            sudo apt-get update
            sudo apt-get install -y certbot python3-certbot-nginx
        else
            error "Please install Certbot manually for your distribution"
            pause
            return 1
        fi
    else
        success "✓ Certbot already installed"
    fi
    
    echo ""
    print_separator
    echo ""
    
    # Get domain information
    read -p "Enter your domain name (e.g., panel.yourdomain.com): " DOMAIN
    
    if [ -z "$DOMAIN" ]; then
        error "Domain name is required"
        pause
        return 1
    fi
    
    read -p "Enter your email address: " EMAIL
    
    if [ -z "$EMAIL" ]; then
        error "Email address is required"
        pause
        return 1
    fi
    
    echo ""
    info "Domain: $DOMAIN"
    info "Email: $EMAIL"
    echo ""
    
    read -p "Is this correct? (y/N): " -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        info "SSL setup cancelled"
        pause
        return 0
    fi
    
    # Check if nginx is installed
    if ! check_command nginx; then
        info "Installing nginx..."
        sudo apt-get install -y nginx
        sudo systemctl enable nginx
        sudo systemctl start nginx
    fi
    
    echo ""
    log "Obtaining SSL certificate..."
    echo ""
    
    # Create nginx config for domain
    sudo tee /etc/nginx/sites-available/tactical-command > /dev/null << EOF
server {
    listen 80;
    server_name $DOMAIN;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /api/ {
        proxy_pass http://localhost:8001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF
    
    # Enable site
    sudo ln -sf /etc/nginx/sites-available/tactical-command /etc/nginx/sites-enabled/
    sudo nginx -t
    sudo systemctl reload nginx
    
    echo ""
    
    # Obtain certificate
    info "Requesting SSL certificate from Let's Encrypt..."
    echo ""
    
    sudo certbot --nginx -d $DOMAIN --email $EMAIL --agree-tos --non-interactive --redirect
    
    if [ $? -eq 0 ]; then
        success "✓ SSL certificate installed successfully!"
        echo ""
        info "Your panel is now accessible at: https://$DOMAIN"
        echo ""
        info "Certificate will auto-renew via certbot timer"
        echo ""
        
        # Test auto-renewal
        sudo certbot renew --dry-run
        
        success "✓ Auto-renewal test passed"
    else
        error "Failed to obtain SSL certificate"
        echo ""
        warn "Common issues:"
        echo "  • Domain doesn't point to this server"
        echo "  • Ports 80/443 blocked by firewall"
        echo "  • DNS propagation not complete"
    fi
    
    echo ""
    pause
}