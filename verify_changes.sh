#!/bin/bash

echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║         Tactical Command - Change Verification Report             ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""

# Test 1: Verify install-functions.sh has auto-install logic
echo "📋 Test 1: Checking install-functions.sh modifications..."
if grep -q "Would you like to install missing dependencies automatically" /app/scripts/install-functions.sh; then
    echo "   ✅ Auto-install prompt added"
else
    echo "   ❌ Auto-install prompt missing"
fi

if grep -q "Installing Python 3..." /app/scripts/install-functions.sh; then
    echo "   ✅ Python auto-install logic added"
else
    echo "   ❌ Python auto-install logic missing"
fi

if grep -q "Installing Node.js..." /app/scripts/install-functions.sh; then
    echo "   ✅ Node.js auto-install logic added"
else
    echo "   ❌ Node.js auto-install logic missing"
fi

if grep -q "setup_18.x" /app/scripts/install-functions.sh; then
    echo "   ✅ NodeSource repository configuration added"
else
    echo "   ❌ NodeSource repository configuration missing"
fi

# Test 2: Verify documentation updates
echo ""
echo "📚 Test 2: Checking documentation updates..."

if grep -q "Auto-installs Python 3 & Node.js" /app/README.md; then
    echo "   ✅ README.md updated"
else
    echo "   ❌ README.md not updated"
fi

if grep -q "Auto-install Python 3" /app/INSTALLATION_GUIDE.md; then
    echo "   ✅ INSTALLATION_GUIDE.md updated"
else
    echo "   ❌ INSTALLATION_GUIDE.md not updated"
fi

if grep -q "NEW.*Auto-installs" /app/INSTALLER_GUIDE.md; then
    echo "   ✅ INSTALLER_GUIDE.md updated"
else
    echo "   ❌ INSTALLER_GUIDE.md not updated"
fi

# Test 3: Check new files
echo ""
echo "📄 Test 3: Checking new documentation files..."

if [ -f /app/CHANGELOG.md ]; then
    echo "   ✅ CHANGELOG.md created"
else
    echo "   ❌ CHANGELOG.md missing"
fi

if [ -f /app/QUICK_INSTALL.md ]; then
    echo "   ✅ QUICK_INSTALL.md created"
else
    echo "   ❌ QUICK_INSTALL.md missing"
fi

# Test 4: Syntax validation
echo ""
echo "🔍 Test 4: Validating bash syntax..."

if bash -n /app/scripts/install.sh 2>/dev/null; then
    echo "   ✅ install.sh syntax valid"
else
    echo "   ❌ install.sh has syntax errors"
fi

if bash -n /app/scripts/install-functions.sh 2>/dev/null; then
    echo "   ✅ install-functions.sh syntax valid"
else
    echo "   ❌ install-functions.sh has syntax errors"
fi

# Test 5: Check for both Ubuntu and RHEL support
echo ""
echo "🐧 Test 5: Checking distribution support..."

if grep -q "/etc/debian_version" /app/scripts/install-functions.sh && \
   grep -q "/etc/redhat-release" /app/scripts/install-functions.sh; then
    echo "   ✅ Multi-distribution support (Debian/Ubuntu + RHEL/CentOS)"
else
    echo "   ❌ Missing multi-distribution support"
fi

# Summary
echo ""
echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║                        Summary of Changes                          ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""
echo "Modified Files:"
echo "  • /app/scripts/install-functions.sh - Added auto-install logic"
echo "  • /app/README.md - Updated with new feature"
echo "  • /app/INSTALLATION_GUIDE.md - Added auto-install details"
echo "  • /app/INSTALLER_GUIDE.md - Updated installation flow"
echo ""
echo "New Files:"
echo "  • /app/CHANGELOG.md - Version history and changes"
echo "  • /app/QUICK_INSTALL.md - Quick reference guide"
echo ""
echo "Features Added:"
echo "  ✨ Automatic Python 3.11+ installation"
echo "  ✨ Automatic Node.js 18.x installation"
echo "  ✨ NodeSource repository integration"
echo "  ✨ Multi-distribution support (Debian/Ubuntu, RHEL/CentOS)"
echo "  ✨ User prompts before installation"
echo "  ✨ Installation verification"
echo ""
echo "User Benefits:"
echo "  🎯 No more manual dependency installation"
echo "  🎯 Single command setup: ./install.sh"
echo "  🎯 Automatic detection and installation"
echo "  🎯 Works on most Linux distributions"
echo ""
