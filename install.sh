#!/bin/bash
set -e

APP_NAME="gasReport"
INSTALL_DIR="$HOME/.local/bin"
REPO_PATH="$(pwd)"
APP_PATH="$REPO_PATH/app.py"
WRAPPER_PATH="$INSTALL_DIR/$APP_NAME"

# 1. Ensure ~/.local/bin exists
mkdir -p "$INSTALL_DIR"

# 2. Prepare new wrapper content with absolute repo path
read -r -d '' NEW_WRAPPER <<EOF || true
#!/bin/bash
cd "$REPO_PATH"
source .venv/bin/activate
python3 app.py
EOF

# 3. Write wrapper only if content differs or file missing
if [ ! -f "$WRAPPER_PATH" ] || ! cmp -s <(echo "$NEW_WRAPPER") "$WRAPPER_PATH"; then
    echo "$NEW_WRAPPER" > "$WRAPPER_PATH"
    chmod +x "$WRAPPER_PATH"
    echo "Updated wrapper script at $WRAPPER_PATH"
fi

# 4. Make sure ~/.local/bin is in PATH in .bashrc (avoid duplicates)
if ! grep -Fxq 'export PATH="$HOME/.local/bin:$PATH"' "$HOME/.bashrc"; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
    echo "Added ~/.local/bin to PATH in ~/.bashrc"
fi

# 5. Check python version (warn only)
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
MIN_VERSION="3.8"
if [[ "$(printf '%s\n' "$MIN_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$MIN_VERSION" ]]; then
    echo "Warning: Your Python version ($PYTHON_VERSION) might be too old. Recommended 3.8+."
fi

# 6. Set up .venv & install deps if missing
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo ".venv already exists. Skipping dependency installation."
fi

echo ""
echo "Install complete! Remember to restart your terminal or run:"
echo "  source ~/.bashrc"
echo "to refresh your PATH and use the '$APP_NAME' command from anywhere."
echo ""
echo "Run the app anytime by typing:"
echo "  $APP_NAME"
