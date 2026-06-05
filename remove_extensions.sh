#!/bin/bash

# ─────────────────────────────────────────────
#  GNOME Extension Full Cleanup Script
#  Fedora / GNOME — disables + deletes all
#  user-installed extensions automatically
# ─────────────────────────────────────────────

set -euo pipefail

echo ""
echo "======================================"
echo "  GNOME Extension Cleanup — Starting  "
echo "======================================"
echo ""

# ── Step 1: Show currently enabled extensions ──
echo "[INFO] Currently enabled extensions:"
gsettings get org.gnome.shell enabled-extensions
echo ""

# ── Step 2: Disable ALL enabled extensions ──
echo "[INFO] Disabling all enabled extensions..."
gsettings set org.gnome.shell enabled-extensions "[]"
echo "[OK]  All extensions disabled in gsettings."
echo ""

# ── Step 3: List and delete user extensions ──
USER_EXT_DIR="$HOME/.local/share/gnome-shell/extensions"

if [ -d "$USER_EXT_DIR" ]; then
    echo "[INFO] Extensions found in: $USER_EXT_DIR"
    echo ""

    # Count how many exist
    EXT_COUNT=$(ls -1 "$USER_EXT_DIR" 2>/dev/null | wc -l)

    if [ "$EXT_COUNT" -eq 0 ]; then
        echo "[INFO] No user extensions found in directory."
    else
        echo "[INFO] Found $EXT_COUNT extension(s) to remove:"
        ls -1 "$USER_EXT_DIR"
        echo ""

        # Delete each one
        for ext in "$USER_EXT_DIR"/*/; do
            if [ -d "$ext" ]; then
                echo "[DEL]  Removing: $ext"
                rm -rf "$ext"
            fi
        done
        echo ""
        echo "[OK]  All user extensions deleted."
    fi
else
    echo "[INFO] No user extension directory found. Skipping."
fi

echo ""

# ── Step 4: Remove system-wide extensions (optional, needs sudo) ──
SYS_EXT_DIR="/usr/share/gnome-shell/extensions"

echo "[INFO] Checking system-wide extensions (requires sudo)..."
if [ -d "$SYS_EXT_DIR" ]; then
    SYS_COUNT=$(ls -1 "$SYS_EXT_DIR" 2>/dev/null | wc -l)
    if [ "$SYS_COUNT" -gt 0 ]; then
        echo "[INFO] System extensions found:"
        ls -1 "$SYS_EXT_DIR"
        echo ""
        read -p "Delete system-wide extensions too? (y/N): " CONFIRM
        if [[ "$CONFIRM" =~ ^[Yy]$ ]]; then
            sudo rm -rf "$SYS_EXT_DIR"/*
            echo "[OK]  System extensions removed."
        else
            echo "[SKIP] System extensions kept."
        fi
    else
        echo "[INFO] No system extensions found."
    fi
else
    echo "[INFO] No system extension directory found."
fi

echo ""

# ── Step 5: Remove gnome-shell-extensions package (if installed) ──
echo "[INFO] Checking for gnome-shell-extensions package..."
if rpm -q gnome-shell-extensions &>/dev/null; then
    echo "[FOUND] gnome-shell-extensions package is installed."
    read -p "Remove the gnome-shell-extensions RPM package? (y/N): " CONFIRM2
    if [[ "$CONFIRM2" =~ ^[Yy]$ ]]; then
        sudo dnf remove -y gnome-shell-extensions
        echo "[OK]  Package removed."
    else
        echo "[SKIP] Package kept."
    fi
else
    echo "[INFO] gnome-shell-extensions package not installed."
fi

echo ""

# ── Step 6: Clear extension cache ──
echo "[INFO] Clearing GNOME Shell extension cache..."
rm -rf "$HOME/.cache/gnome-shell/extensions" 2>/dev/null && \
    echo "[OK]  Cache cleared." || \
    echo "[INFO] No cache to clear."

echo ""

# ── Step 7: Final verification ──
echo "[INFO] Verifying — remaining enabled extensions:"
gsettings get org.gnome.shell enabled-extensions
echo ""

echo "======================================"
echo "  Cleanup complete!"
echo "  Please log out and log back in,"
echo "  or run: gnome-shell --replace &"
echo "======================================"
echo ""
