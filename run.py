"""
run.py — Single-command launcher for VisionAI.

Usage:
    python run.py           # checks Ollama + builds frontend + starts server
    python run.py --dev     # skips frontend build (assumes already built)
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

ROOT = Path(__file__).parent
FRONTEND = ROOT / "frontend"
BACKEND = ROOT / "backend"
STATIC = BACKEND / "static"


def is_port_open(port: int = 11434) -> bool:
    """Check if the given port is open on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def ensure_ollama_running() -> bool:
    """Ensure the Ollama local service is running. Starts it if offline."""
    if is_port_open():
        print("✓  Ollama is already running.")
        return True

    print("⚠️  Ollama is not running. Starting 'ollama serve' in background...")
    try:
        creationflags = 0
        if os.name == "nt":
            # CREATE_NO_WINDOW flags to prevent popping up console windows
            creationflags = 0x08000000

        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creationflags,
        )

        # Wait up to 15 seconds for Ollama to boot
        for _ in range(30):
            time.sleep(0.5)
            if is_port_open():
                print("✓  Ollama started successfully.")
                return True
        print("✗  Ollama took too long to start. Please run 'ollama serve' manually.")
        return False
    except Exception as e:
        print(f"✗  Failed to auto-start Ollama: {e}")
        print("Please ensure Ollama is installed and running on port 11434.")
        return False


def ensure_llava_model() -> bool:
    """Check if the LLaVA model is downloaded. Pulls it if absent."""
    model_name = "llava:7b"
    try:
        req = urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=5)
        data = json.loads(req.read().decode("utf-8"))
        models = data.get("models", [])
        downloaded = [m["name"] for m in models]

        # Match exact name or base name
        if any(
            m.startswith(model_name) or model_name.startswith(m.split(":")[0])
            for m in downloaded
        ):
            print(f"✓  Ollama model '{model_name}' is ready.")
            return True

        print(
            f"📥  Model '{model_name}' not found. Downloading it now (approx. 4.7 GB)..."
        )
        print("This may take several minutes depending on your internet connection.")
        # Run pull synchronously so the user sees the native progress bar
        subprocess.run(["ollama", "pull", model_name], check=True)
        print(f"✓  Model '{model_name}' pulled successfully.")
        return True
    except Exception as e:
        print(f"⚠️  Could not verify or pull Ollama model: {e}")
        print(
            f"Please ensure you can run: ollama pull {model_name} in your terminal."
        )
        return False


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
    if STATIC.exists():
        shutil.rmtree(STATIC)
    shutil.copytree(dist, STATIC)
    print(f"✓  Frontend build copied to {STATIC}")


def start_server() -> None:
    print("\n🚀  Starting VisionAI server at http://localhost:8000")
    print("Open your browser and navigate to: http://localhost:8000")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
        ],
        cwd=BACKEND,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="VisionAI launcher")
    parser.add_argument("--dev", action="store_true", help="Skip frontend build")
    args = parser.parse_args()

    print("🛡️  Checking system requirements...")
    if ensure_ollama_running():
        ensure_llava_model()

    if not args.dev:
        build_frontend()

    start_server()


if __name__ == "__main__":
    main()
