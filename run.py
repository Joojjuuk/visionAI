"""
run.py — Single-command launcher for VisionAI.

Usage:
    python run.py           # builds frontend + starts server
    python run.py --dev     # skips frontend build (assumes already built)
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
FRONTEND = ROOT / "frontend"
BACKEND = ROOT / "backend"
STATIC = BACKEND / "static"


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
    print("🚀  Starting VisionAI server at http://localhost:8000")
    subprocess.run(
        [
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--host", "127.0.0.1",
            "--port", "8000",
        ],
        cwd=BACKEND,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="VisionAI launcher")
    parser.add_argument("--dev", action="store_true", help="Skip frontend build")
    args = parser.parse_args()

    if not args.dev:
        build_frontend()

    start_server()


if __name__ == "__main__":
    main()
