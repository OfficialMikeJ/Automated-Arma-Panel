#!/bin/bash

###############################################################################
# Pre-Installation Verification Script
# Run this before installing the panel to check all requirements
###############################################################################

echo "=========================================="
echo "Tactical Command - Pre-Install Check"
echo "=========================================="
echo ""

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d" " -f2)
    echo "✅ Python 3 installed: $PYTHON_VERSION"
else
    echo "❌ Python 3 NOT installed"
fi

# Check python3-venv
if dpkg -l 2>/dev/null | grep -q "python3.*-venv"; then
    echo "✅ python3-venv package installed"
else
    echo "❌ python3-venv NOT installed"
    echo "   → Will be auto-installed by installer"
fi

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js installed: $NODE_VERSION"
else
    echo "❌ Node.js NOT installed"
fi

# Check Yarn
if command -v yarn &> /dev/null; then
    echo "✅ Yarn installed"
else
    echo "❌ Yarn NOT installed"
fi

# Check MongoDB
if command -v mongod &> /dev/null; then
    echo "✅ MongoDB installed"
else
    echo "❌ MongoDB NOT installed"
fi

echo ""
echo "=========================================="
echo "Virtual Environment Test"
echo "=========================================="

# Try to create a test venv
TEST_DIR="/tmp/venv_test_$$"
mkdir -p "$TEST_DIR"

echo "Testing venv creation in $TEST_DIR..."

if python3 -m venv "$TEST_DIR/testvenv" 2>/dev/null; then
    echo "✅ Virtual environment creation works!"
    rm -rf "$TEST_DIR"
else
    echo "❌ Virtual environment creation FAILED!"
    echo ""
    echo "Fix with:"
    echo "  sudo apt-get install -y python3-venv"
    echo ""
fi

echo ""
echo "=========================================="
echo "Recommendation"
echo "=========================================="
echo ""

# Count issues
ISSUES=0

command -v python3 &> /dev/null || ((ISSUES++))
command -v node &> /dev/null || ((ISSUES++))
command -v mongod &> /dev/null || ((ISSUES++))
dpkg -l 2>/dev/null | grep -q "python3.*-venv" || ((ISSUES++))

if [ $ISSUES -eq 0 ]; then
    echo "✅ All requirements met! You can run the installer."
    echo ""
    echo "Run: sudo bash ./install.sh"
else
    echo "⚠️  $ISSUES requirement(s) missing"
    echo ""
    echo "The installer will auto-install missing components."
    echo "Or install manually:"
    echo ""
    [ ! command -v python3 &> /dev/null ] && echo "  sudo apt-get install -y python3 python3-pip python3-venv"
    [ ! command -v node &> /dev/null ] && echo "  # Node.js will be auto-installed by installer"
    [ ! command -v mongod &> /dev/null ] && echo "  # MongoDB will be prompted during installation"
    dpkg -l 2>/dev/null | grep -q "python3.*-venv" || echo "  sudo apt-get install -y python3-venv"
    echo ""
    echo "Then run: sudo bash ./install.sh"
fi

echo ""
