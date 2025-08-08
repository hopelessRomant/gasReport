#!/usr/bin/env bash
set -e

APP_NAME="GasReport"
ICON_FILE="gasReport.jpg" # must be in same folder as install.sh
SCRIPT_TO_RUN="./run.sh"  # entry point of your app

# --- Detect Windows username ---
WIN_USER=$(cmd.exe /C "echo %USERNAME%" 2>/dev/null | tr -d '\r')

# --- Paths ---
LINUX_DESKTOP_DIR="$HOME/.local/share/applications"
WIN_ICON_DIR="/mnt/c/Users/$WIN_USER/Pictures/$APP_NAME"
WIN_ICON_PATH="$WIN_ICON_DIR/$ICON_FILE"
DESKTOP_FILE="$LINUX_DESKTOP_DIR/$APP_NAME.desktop"

# --- Create directories ---
mkdir -p "$LINUX_DESKTOP_DIR"
mkdir -p "$WIN_ICON_DIR"

# --- Copy icon to Windows-accessible path ---
if [[ ! -f "$ICON_FILE" ]]; then
    echo "[ERROR] Icon file '$ICON_FILE' not found in $(pwd)"
    exit 1
fi
cp "$ICON_FILE" "$WIN_ICON_PATH"

# --- Create desktop shortcut (used by WSLg & Windows Start Menu) ---
cat > "$DESKTOP_FILE" <<EOL
[Desktop Entry]
Name=$APP_NAME
Exec=/bin/bash -c "cd $(pwd) && $SCRIPT_TO_RUN"
Icon=$WIN_ICON_PATH
Type=Application
Categories=Utility;
Terminal=false
EOL

# --- Make shortcut executable ---
chmod +x "$DESKTOP_FILE"

# --- Refresh Windows Start Menu ---
powershell.exe -Command "Stop-Process -Name explorer -Force; Start-Process explorer" >/dev/null 2>&1 || true

echo "[SUCCESS] '$APP_NAME' installed."
echo " - Shortcut: $DESKTOP_FILE"
echo " - Icon: $WIN_ICON_PATH"
echo "You can now find '$APP_NAME' in the Windows Start Menu and Linux app list."
