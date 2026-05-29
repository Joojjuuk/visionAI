"""
run.py — Single-command launcher for VisionAI.

Usage:
    python run.py           # builds frontend + starts server (YOLOv8 + Google Gemini)
    python run.py --dev     # skips frontend build (assumes already built)
    python run.py --local   # offline mode: YOLOv8 + local computer-vision (no Gemini)
"""
import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

# Force UTF-8 encoding for standard output to avoid UnicodeEncodeErrors on Windows terminals
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT = Path(__file__).parent
FRONTEND = ROOT / "frontend"
BACKEND = ROOT / "backend"
STATIC = BACKEND / "static"


def is_port_open(port: int) -> bool:
    """Check if the given port is open on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def build_frontend() -> None:
    print("⚙  Building frontend…")
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=FRONTEND,
        shell=True,
    )
    if result.returncode != 0:
        print("✗  Frontend build failed.", file=sys.stderr)
        sys.exit(1)

    dist = FRONTEND / "dist"
    try:
        # Robust cleanup: try to delete individual files without crashing on locked directories
        if STATIC.exists():
            for item in STATIC.iterdir():
                try:
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
                except Exception:
                    pass  # locked by running uvicorn instances, skip gracefully

        # Copy the new assets merging with existing
        shutil.copytree(dist, STATIC, dirs_exist_ok=True)
        print(f"✓  Frontend build copied to {STATIC}")
    except Exception as e:
        print(f"\n⚠️  Warning while copying assets: {e}")
        print("This is normal if uvicorn is running in another terminal.")
        print("Please close any other running python/uvicorn processes and run again.")
        print("Continuing launcher run...")


def start_server() -> None:
    print("\n🚀  Starting VisionAI server at http://localhost:8000")
    print("Open your browser and navigate to: http://localhost:8000")

    # Search for uvicorn in common virtual environment locations
    venv_paths = [
        ROOT / ".venv" / "Scripts" / "uvicorn.exe",
        ROOT / ".venv" / "bin" / "uvicorn",
        BACKEND / ".venv" / "Scripts" / "uvicorn.exe",
        BACKEND / ".venv" / "bin" / "uvicorn",
    ]

    uvicorn_cmd = None
    for path in venv_paths:
        if path.exists():
            uvicorn_cmd = str(path)
            print(f"✓  Using virtual environment uvicorn: {uvicorn_cmd}")
            break

    if not uvicorn_cmd:
        # Fallback 1: check if uvicorn is in PATH as a command
        if shutil.which("uvicorn"):
            uvicorn_cmd = "uvicorn"
        else:
            # Fallback 2: fallback to global uvicorn command directly
            uvicorn_cmd = "uvicorn"
            print(
                "⚠️  uvicorn not found in active virtual env. Trying global 'uvicorn' command..."
            )

    try:
        # shell=True is critical on Windows to execute uvicorn via system PATH
        subprocess.run(
            [
                uvicorn_cmd,
                "app.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                "8000",
            ],
            cwd=BACKEND,
            shell=True if uvicorn_cmd == "uvicorn" else False,
        )
    except Exception as e:
        print(f"\n✗  Failed to run uvicorn server: {e}")
        print(
            "Please make sure your Python virtual environment is active or uvicorn is installed."
        )
        print("You can also run directly: cd backend && uvicorn app.main:app")


def main() -> None:
    parser = argparse.ArgumentParser(description="VisionAI launcher")
    parser.add_argument("--dev", action="store_true", help="Skip frontend build")
    parser.add_argument(
        "--local",
        action="store_true",
        help="Offline mode: YOLOv8 + local computer-vision instead of Google Gemini",
    )
    args = parser.parse_args()

    use_local = args.local or os.environ.get("DETECTION_MODE", "").lower() == "yolo"
    if use_local:
        os.environ["DETECTION_MODE"] = "yolo"
        print("🛡️  Detection mode: LOCAL (YOLOv8 + computer-vision, offline)")
    else:
        os.environ["DETECTION_MODE"] = "gemini"
        print("🛡️  Detection mode: GEMINI (YOLOv8 + Google Gemini 2.5 Flash)")

    print("Checking system requirements...")

    # Detect if the server is already active on port 8000
    if is_port_open(8000):
        print("\n💡  VisionAI server is already active on http://localhost:8000 !")
        print("🚀  No need to start another instance. Just open http://localhost:8000 in your browser.")
        return

    if not args.dev:
        build_frontend()

    start_server()


if __name__ == "__main__":
    main()

