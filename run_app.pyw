#!/usr/bin/env pythonw
"""
Double-click launcher for the DV360 reporting app (no console window).
Writes all output and any errors to run_app.log next to this file, so a
silent failure can be diagnosed: if nothing happens, open run_app.log.
"""

import os
import shutil
import subprocess
import sys
import time
import traceback
import webbrowser
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOG = HERE / "run_app.log"
PORT = "8501"


def log(msg: str) -> None:
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"{msg}\n")


try:
    # Start a fresh log each launch.
    LOG.write_text(f"--- launch {time.ctime()} ---\ncwd={HERE}\n", encoding="utf-8")

    # Credentials: load from gitignored local_settings.py if present,
    # otherwise rely on persistent Windows env vars.
    settings = HERE / "local_settings.py"
    if settings.exists():
        ns: dict = {}
        exec(settings.read_text(), ns)  # noqa: S102 - trusted local file you control
        for key in ("GOOGLE_APPLICATION_CREDENTIALS", "ANTHROPIC_API_KEY"):
            if ns.get(key):
                os.environ[key] = str(ns[key])
        log("loaded local_settings.py")
    else:
        log("no local_settings.py found - using system environment variables")

    # Locate uv (double-click often can't see it on PATH).
    uv = shutil.which("uv")
    if not uv:
        for cand in (
            Path(os.environ.get("USERPROFILE", "")) / ".local" / "bin" / "uv.exe",
            Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "uv" / "uv.exe",
            Path(os.environ.get("APPDATA", "")) / "uv" / "uv.exe",
        ):
            if cand.exists():
                uv = str(cand)
                break
    if not uv:
        log("ERROR: could not find 'uv'. Open cmd and run `where uv`, then put "
            "its full path on the UV line below.")
        sys.exit(1)
    log(f"using uv: {uv}")

    no_window = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    logf = open(LOG, "a", encoding="utf-8")
    proc = subprocess.Popen(
        [uv, "run", "streamlit", "run", "app.py",
         "--server.headless=true", f"--server.port={PORT}"],
        cwd=str(HERE),
        creationflags=no_window,
        stdout=logf,
        stderr=logf,
    )
    log(f"started streamlit (pid={proc.pid}); opening browser in 6s")
    time.sleep(6)
    webbrowser.open(f"http://localhost:{PORT}")
    proc.wait()
except Exception:
    log("EXCEPTION:\n" + traceback.format_exc())
