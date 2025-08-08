#!/bin/bash
set -e

APP_NAME="gasReport"
INSTALL_DIR="$HOME/.local/bin"
APP_PATH="$(pwd)/app.py"
WRAPPER_PATH="$INSTALL_DIR/$APP_NAME"

# 1. Ensure ~/.local/bin exists
mkdir -p "$INSTALL_DIR"

# 2. Prepare new wrapper content
read -r -d '' NEW_WRAPPER <<EOF || true
#!/bin/bash
cd "$(pwd)"
source .venv/bin/activate
python3 "$APP_PATH"
EOF

# 3. Write wrapper only if content differs or file missing
if [ ! -f "$WRAPPER_PATH" ] || ! cmp -s <(echo "$NEW_WRAPPER") "$WRAPPER_PATH"; then
    echo "$NEW_WRAPPER" > "$WRAPPER_PATH"
    chmod +x "$WRAPPER_PATH"
    echo "Updated wrapper script at $WRAPPER_PATH"
fi

# 4. Make sure ~/.local/bin is in PATH
if ! echo "$PATH" | grep -q "$HOME/.local/bin"; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
    export PATH="$HOME/.local/bin:$PATH"
fi

# 5. Set up .venv & install deps if missing
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

# 6. Launch the app
python3 "$APP_PATH"
