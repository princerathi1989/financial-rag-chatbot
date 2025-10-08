#!/usr/bin/env python3
"""
Unified launcher for the Financial Chatbot (backend + frontend).

Usage:
  python start_chatbot.py [--no-frontend] [--api-port 8000] [--ui-port 8501] [--host 0.0.0.0]

This script sets PYTHONPATH for the backend, starts the FastAPI app (uvicorn),
and optionally starts the Streamlit UI.
"""
import argparse
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
import shutil


def extend_pythonpath(path: str) -> None:
    current = os.environ.get("PYTHONPATH", "")
    if current:
        os.environ["PYTHONPATH"] = f"{path}:{current}"
    else:
        os.environ["PYTHONPATH"] = path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Start backend and Streamlit UI")
    parser.add_argument("--no-frontend", action="store_true", help="Do not start Streamlit UI")
    parser.add_argument("--api-port", type=int, default=8000, help="Port for the FastAPI server")
    parser.add_argument("--ui-port", type=int, default=8501, help="Port for the Streamlit UI")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host interface for FastAPI")
    parser.add_argument("--reload", action="store_true", help="Enable uvicorn auto-reload")
    return parser.parse_args()


def main() -> int:
    repo_root = Path(__file__).resolve().parent
    backend_app_path = repo_root / "backend" / "app"
    uvicorn_app_module = "backend.uvicorn_app:app"
    streamlit_app_path = repo_root / "frontend" / "app.py"

    # Ensure backend is importable
    extend_pythonpath(str(repo_root / "backend"))

    args = parse_args()

    # Clear uploads directory on startup (recreated via ensure_directories)
    try:
        from backend.app.core.config import settings, ensure_directories
        uploads_dir = Path(settings.upload_directory)
        if uploads_dir.exists():
            shutil.rmtree(uploads_dir, ignore_errors=True)
        ensure_directories()
    except Exception as e:
        print(f"Warning: failed to reset uploads directory: {e}")

    # Build uvicorn command
    uvicorn_cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        uvicorn_app_module,
        "--host",
        args.host,
        "--port",
        str(args.api_port),
    ]
    if args.reload:
        uvicorn_cmd.append("--reload")

    processes = []
    try:
        # Start backend (FastAPI)
        backend_proc = subprocess.Popen(uvicorn_cmd, cwd=str(repo_root))
        processes.append(("backend", backend_proc))

        # Optionally start Streamlit
        if not args.no_frontend:
            if not streamlit_app_path.exists():
                print(f"Streamlit app not found at {streamlit_app_path}")
            else:
                streamlit_cmd = [
                    sys.executable,
                    "-m",
                    "streamlit",
                    "run",
                    str(streamlit_app_path),
                    "--server.port",
                    str(args.ui_port),
                ]
                frontend_proc = subprocess.Popen(streamlit_cmd, cwd=str(repo_root))
                processes.append(("frontend", frontend_proc))

        # Wait and forward signals
        def handle_signal(signum, frame):
            for name, proc in processes:
                try:
                    proc.terminate()
                except Exception:
                    pass
            time.sleep(0.5)
            for name, proc in processes:
                try:
                    proc.kill()
                except Exception:
                    pass

        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)

        # Monitor processes
        while True:
            alive = False
            for name, proc in processes:
                ret = proc.poll()
                if ret is None:
                    alive = True
                else:
                    print(f"{name} exited with code {ret}")
                    # If backend dies, stop frontend too
                    if name == "backend":
                        handle_signal(signal.SIGTERM, None)
                        return ret if ret is not None else 1
            if not alive:
                return 0
            time.sleep(0.5)
    finally:
        for name, proc in processes:
            try:
                proc.terminate()
            except Exception:
                pass

    return 0


if __name__ == "__main__":
    sys.exit(main())


