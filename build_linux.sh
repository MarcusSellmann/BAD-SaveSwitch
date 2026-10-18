#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

python3 -m venv build/linux-venv
build/linux-venv/bin/python -m pip install -r requirements-build.txt
build/linux-venv/bin/python -m PyInstaller \
    --noconfirm \
    --clean \
    --onefile \
    --add-data "assets/BAD_Save_Switch.ico:assets" \
    --name BAD-SaveSwitch \
    --distpath dist \
    --workpath build/pyinstaller-linux \
    --specpath build/linux \
    main.py

printf '\nBuilt dist/BAD-SaveSwitch\n'