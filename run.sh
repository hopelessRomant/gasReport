#!/bin/bash
# Create and activate virtualenv if not exists
if [ ! -d "venv" ]; then
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

# Run the PyQt6 app
python3 app.py
