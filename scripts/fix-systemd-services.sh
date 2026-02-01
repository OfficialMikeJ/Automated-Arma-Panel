#!/bin/bash

###############################################################################
# Automated Systemd Service Fix Script
# This script fixes systemd services with correct paths
###############################################################################

echo "=========================================="
echo "Fixing Systemd Services"
echo "=========================================="

# Get the installation directory
INSTALL_DIR="/opt/Automated-Arma-Panel-main"

if [ ! -d "$INSTALL_DIR" ]; then
    echo "ERROR: Installation directory not found at $INSTALL_DIR"
    echo "Please update INSTALL_DIR in this script to match your installation path"
    exit 1
fi

echo "Step 1: Stopping services..."
sudo systemctl stop tactical-backend tactical-frontend 2>/dev/null

echo "Step 2: Removing old service files..."
sudo rm -f /etc/systemd/system/tactical-backend.service
sudo rm -f /etc/systemd/system/tactical-frontend.service

echo "Step 3: Creating backend service..."
sudo tee /etc/systemd/system/tactical-backend.service > /dev/null << EOF
[Unit]
Description=Tactical Command Backend Service
After=network.target mongodb.service
Wants=mongodb.service

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=$INSTALL_DIR/backend

ExecStart=$INSTALL_DIR/backend/venv/bin/python -m uvicorn server:app --host 0.0.0.0 --port 8001 --workers 1

Restart=always
RestartSec=10

StandardOutput=journal
StandardError=journal
SyslogIdentifier=tactical-backend

LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
EOF

echo "Step 4: Creating frontend service..."
sudo tee /etc/systemd/system/tactical-frontend.service > /dev/null << EOF
[Unit]
Description=Tactical Command Frontend Service
After=network.target tactical-backend.service
Wants=tactical-backend.service

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=$INSTALL_DIR/frontend

Environment="HOST=0.0.0.0"
Environment="PORT=3000"

ExecStart=/usr/bin/yarn start

Restart=always
RestartSec=10

StandardOutput=journal
StandardError=journal
SyslogIdentifier=tactical-frontend

LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
EOF

echo "Step 5: Reloading systemd..."
sudo systemctl daemon-reload

echo "Step 6: Enabling services..."
sudo systemctl enable tactical-backend tactical-frontend

echo "Step 7: Starting services..."
sudo systemctl start tactical-backend tactical-frontend

echo "Step 8: Waiting for services to start..."
sleep 5

echo ""
echo "=========================================="
echo "Service Status:"
echo "=========================================="
sudo systemctl status tactical-backend --no-pager -l
echo ""
sudo systemctl status tactical-frontend --no-pager -l

echo ""
echo "=========================================="
echo "Done! Services should be running."
echo "Access your panel at: http://YOUR_IP:3000"
echo "=========================================="
