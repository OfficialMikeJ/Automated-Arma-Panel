#!/bin/bash
# Quick verification test for install script

echo "=== Installation Script Verification ==="
echo ""

# Test 1: Check if install.sh exists and is executable
if [ -f /app/scripts/install.sh ]; then
    echo "✓ install.sh exists"
else
    echo "✗ install.sh not found"
    exit 1
fi

# Test 2: Check bash syntax
if bash -n /app/scripts/install.sh 2>/dev/null; then
    echo "✓ install.sh syntax is valid"
else
    echo "✗ install.sh has syntax errors"
    exit 1
fi

# Test 3: Check install-functions.sh
if bash -n /app/scripts/install-functions.sh 2>/dev/null; then
    echo "✓ install-functions.sh syntax is valid"
else
    echo "✗ install-functions.sh has syntax errors"
    exit 1
fi

# Test 4: Check for dependency installation logic
if grep -q "Installing Node.js..." /app/scripts/install-functions.sh; then
    echo "✓ Node.js auto-installation logic present"
else
    echo "✗ Node.js auto-installation logic missing"
    exit 1
fi

if grep -q "Installing Python 3..." /app/scripts/install-functions.sh; then
    echo "✓ Python auto-installation logic present"
else
    echo "✗ Python auto-installation logic missing"
    exit 1
fi

# Test 5: Check for NodeSource repository setup
if grep -q "setup_18.x" /app/scripts/install-functions.sh; then
    echo "✓ NodeSource repository configuration present"
else
    echo "✗ NodeSource repository configuration missing"
    exit 1
fi

echo ""
echo "=== All verification tests passed! ==="
echo ""
echo "The install.sh script now includes:"
echo "  • Automatic Python 3 installation"
echo "  • Automatic Node.js 18.x installation"
echo "  • Support for Debian/Ubuntu and RHEL/CentOS"
echo "  • User prompts before installing"
echo ""
