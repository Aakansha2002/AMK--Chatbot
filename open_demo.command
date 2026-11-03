#!/bin/bash
set -e
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"
if [ -f "$PROJECT_DIR/.env" ]; then
  set -a
  . "$PROJECT_DIR/.env"
  set +a
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is required. Install Python 3, then double-click this file again."
  read -r -p "Press Return to close this window..."
  exit 1
fi

if [ ! -x "$PROJECT_DIR/.venv/bin/python" ] || ! "$PROJECT_DIR/.venv/bin/python" -c 'import sys' >/dev/null 2>&1; then
  echo "Preparing the private Python environment (first run only)..."
  python3 -m venv --clear "$PROJECT_DIR/.venv"
fi
PYTHON="$PROJECT_DIR/.venv/bin/python"

if ! "$PYTHON" -c 'import django' >/dev/null 2>&1; then
  echo "Installing the app dependency (first run only)..."
  if ! "$PYTHON" -m pip install -r requirements.txt; then
    echo "Dependency setup failed. Check your internet connection and try again."
    read -r -p "Press Return to close this window..."
    exit 1
  fi
fi

"$PYTHON" manage.py migrate
echo "Starting AMK Hospitality. Keep this Terminal window open while using the demo."
(sleep 2; open -a "Google Chrome" "http://127.0.0.1:8000") &
exec "$PYTHON" manage.py runserver 127.0.0.1:8000
