#!/usr/bin/env python3
"""
Prima Engine — Install / Update / Run script.

Usage:
    python install.py install       Install from local source
    python install.py update        Pull latest from git + reinstall
    python install.py run           Launch the editor
    python install.py server        Start a game server
    python install.py --help        Show this help
"""

import os
import sys
import subprocess
import platform
import shutil

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
REQUIREMENTS = [
    "numpy",
    "PyOpenGL",
    "PyQt5",
    "scikit-build-core>=0.10.0",
    "nanobind>=2.0.0",
]


def check_python():
    if sys.version_info < (3, 10):
        print("[!] Python 3.10+ required")
        sys.exit(1)
    print(f"[✓] Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")


def run(cmd, cwd=None, capture=False):
    print(f"  $ {' '.join(cmd)}")
    kwargs = {"cwd": cwd or PROJECT_DIR}
    if capture:
        return subprocess.run(cmd, check=True, capture_output=True, text=True, **kwargs)
    subprocess.run(cmd, check=True, **kwargs)


def cmd_install():
    check_python()

    print("\n[1/4] Installing Python dependencies...")
    pip = [sys.executable, "-m", "pip", "install"]
    run(pip + REQUIREMENTS)

    print("\n[2/4] Building C++ physics module...")
    run([sys.executable, "-m", "pip", "install", "-e", ".", "--no-build-isolation"])

    print("\n[3/4] Verifying installation...")
    try:
        from prima.engine._physics import PhysicsWorld
        print("[✓] C++ physics module loaded")
    except ImportError as e:
        print(f"[!] Physics module not available: {e}")

    try:
        from prima.engine import Engine
        from prima.server import GameServer
        from prima.client import GameWindow
        print("[✓] All Python modules import correctly")
    except ImportError as e:
        print(f"[!] Import error: {e}")
        sys.exit(1)

    print("\n[4/4] Creating desktop entry...")
    _create_desktop_entry()
    print("\n[✓] Prima Engine installed successfully")
    print("    Run:  python install.py run")
    print("    Or:   python main.py")


def cmd_update():
    print("\n[1/2] Pulling latest source from git...")
    run(["git", "pull"])

    print("\n[2/2] Rebuilding...")
    cmd_install()


def cmd_run():
    print("Launching Prima Editor...")
    os.chdir(PROJECT_DIR)
    run([sys.executable, "main.py"])


def cmd_server():
    print("Launching Prima Server...")
    os.chdir(PROJECT_DIR)
    run([sys.executable, "-m", "prima.server.cli"] + sys.argv[2:])


def _create_desktop_entry():
    if platform.system() != "Linux":
        return
    desktop_dir = os.path.expanduser("~/.local/share/applications")
    os.makedirs(desktop_dir, exist_ok=True)
    icon_path = os.path.join(PROJECT_DIR, "prima", "assets", "icon.png")
    entry = f"""[Desktop Entry]
Type=Application
Name=Prima Engine
Comment=3D Game Engine
Exec={sys.executable} {os.path.join(PROJECT_DIR, 'main.py')}
Icon={icon_path if os.path.exists(icon_path) else 'applications-graphics'}
Terminal=false
Categories=Development;Game;
"""
    path = os.path.join(desktop_dir, "prima-engine.desktop")
    with open(path, "w") as f:
        f.write(entry)
    os.chmod(path, 0o755)
    print(f"[✓] Desktop entry: {path}")


def _init_git():
    if os.path.isdir(os.path.join(PROJECT_DIR, ".git")):
        return
    print("\n[!] No git repo found. Initialize one for updates? [Y/n] ", end="")
    answer = input().strip().lower()
    if answer in ("", "y", "yes"):
        run(["git", "init"])
        run(["git", "checkout", "-b", "main"])
        run(["git", "add", "-A"])
        run(["git", "commit", "-m", "Initial commit"])
        print("\n[✓] Git repo initialized")
        print("    To push to GitHub:")
        print("      1. Create a repo at https://github.com/new")
        print("      2. Run:")
        print(f"         git remote add origin https://github.com/YOUR_USER/prima-engine.git")
        print(f"         git push -u origin main")


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("--help", "-h"):
        print(__doc__.strip())
        return

    command = sys.argv[1]

    if command == "install":
        cmd_install()
    elif command == "update":
        cmd_update()
    elif command == "run":
        cmd_run()
    elif command == "server":
        cmd_server()
    else:
        print(f"Unknown command: {command}")
        print(__doc__.strip())
        sys.exit(1)


if __name__ == "__main__":
    main()
