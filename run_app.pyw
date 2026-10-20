#!/usr/bin/env pythonw
"""
Double-click launcher for the DV360 reporting app — no console window.

Runs under pythonw.exe (via the .pyw extension), so it won't be flagged the
way a .bat is, and nothing shows in the taskbar/console.

Credentials: this cannot read local_settings.bat (that's batch syntax). Use
EITHER of these (pick one):
  1. Persistent Windows user env vars (recommended, set once) — then you don't
     need local_settings.py at all. See README / the chat instructions.
  2. A gitignored local_settings.py next to this file, e.g.:
         GOOGLE_APPLICATION_CREDENTIALS = r"C:\\path\\to\\key.json"
         ANTHROPIC_API_KEY = "sk-ant-..."

To stop the app: close the browser tab and end the "streamlit"/"python"
process in Task Manager (there's no console window to close).
"""

import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

HERE = Path(__file__).resolve().parent
PORT = "8501"

# Option 2 fallback: load credentials from a gitignored local_settings.py.
settings = HERE / "local_settings.py"
if settings.exists():
    ns: dict = {}
    exec(settings.read_text(), ns)  # noqa: S102 - trusted local file you control
    for key in ("GOOGLE_APPLICATION_CREDENTIALS", "ANTHROPIC_API_KEY"):
        if ns.get(key):
            os.environ[key] = str(ns[key])

# Hide the child console window on Windows (0 elsewhere).
no_window = getattr(subprocess, "CREATE_NO_WINDOW", 0)

proc = subprocess.Popen(
    ["uv", "run", "streamlit", "run", "app.py",
     "--server.headless=true", f"--server.port={PORT}"],
    cwd=str(HERE),
    creationflags=no_window,
)

# Give the server a moment to come up, then open the browser ourselves
# (headless mode stops Streamlit from opening it and from the email prompt).
time.sleep(5)
webbrowser.open(f"http://localhost:{PORT}")

proc.wait()
