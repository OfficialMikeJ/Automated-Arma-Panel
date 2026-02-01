#!/bin/bash

echo "=== Script Permissions Verification ==="
echo ""

SCRIPT_DIR="/app/scripts"
ALL_OK=true

# Check each script
for script in install.sh fix-permissions.sh update-panel.sh install-functions.sh setup-systemd.sh backup.sh restore.sh; do
    if [ -f "$SCRIPT_DIR/$script" ]; then
        if [ -x "$SCRIPT_DIR/$script" ]; then
            echo "✓ $script - Executable"
        else
            echo "✗ $script - NOT Executable"
            ALL_OK=false
        fi
    else
        echo "? $script - Not found"
    fi
done

echo ""
if [ "$ALL_OK" = true ]; then
    echo "✅ All scripts are executable!"
else
    echo "❌ Some scripts need fixing. Run:"
    echo "   sudo bash /app/scripts/fix-permissions.sh"
fi
