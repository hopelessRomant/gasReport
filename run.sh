#!/bin/bash
set -e

APP_NAME="gasReport"
INSTALL_DIR="$HOME/.local/bin"
APP_PATH="$(pwd)/app.py"

# 1. Ensure ~/.local/bin exists
mkdir -p "$INSTALL_DIR"

# 2. Create a wrapper script in ~/.local/bin
cat > "$INSTALL_DIR/$APP_NAME" <<EOF
#!/bin/bash
cd "$(pwd)"
source .venv/bin/activate
python3 "$APP_PATH"
EOF

chmod +x "$INSTALL_DIR/$APP_NAME"

# 3. Make sure ~/.local/bin is in PATH
if ! echo "$PATH" | grep -q "$HOME/.local/bin"; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
    export PATH="$HOME/.local/bin:$PATH"
fi

# 4. Set up .venv & install deps if missing
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

# 5. Launch the app
python3 "$APP_PATH"
