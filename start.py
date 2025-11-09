"""Startup script to run both backend and frontend servers."""

import subprocess
import sys
import os
import time
from pathlib import Path


def kill_port(port):
    """Kill any process using the specified port."""
    try:
        if sys.platform == "win32":
            # Find process using the port
            result = subprocess.run(
                f'netstat -ano | findstr :{port}',
                shell=True,
                capture_output=True,
                text=True
            )
            if result.stdout:
                # Extract PID from netstat output
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        try:
                            subprocess.run(f'taskkill /F /PID {pid}', shell=True, capture_output=True)
                            print(f"✅ Killed process on port {port} (PID: {pid})")
                        except BaseException:
                            pass
        else:
            # Linux/Mac
            subprocess.run(f'lsof -ti:{port} | xargs kill -9', shell=True, capture_output=True)
    except BaseException:
        pass


def main():
    """Start both backend and frontend servers."""
    print("=" * 50)
    print("  Followupper - Starting Application")
    print("=" * 50)
    print()

    # Kill any processes on old ports
    print("🧹 Cleaning up old processes...")
    kill_port(3001)
    kill_port(3002)
    kill_port(8001)  # Also kill any old backend instances
    kill_port(4000)  # And frontend port
    time.sleep(1)
    print()

    # Get the project root directory
    project_root = Path(__file__).parent
    frontend_dir = project_root / "frontend"

    # Check if frontend directory exists
    if not frontend_dir.exists():
        print("❌ Error: frontend directory not found!")
        sys.exit(1)

    # Start backend server
    print("🚀 Starting backend server...")

    backend_dir = project_root / "backend"

    if sys.platform == "win32":
        backend_process = subprocess.Popen(
            'uv run python manage.py runserver 0.0.0.0:8001',
            cwd=backend_dir,
            shell=True
        )
    else:
        backend_process = subprocess.Popen(
            'uv run python manage.py runserver 0.0.0.0:8001',
            shell=True,
            cwd=backend_dir
        )

    # Wait a bit for backend to start
    print("⏳ Waiting 3 seconds for backend to initialize...")
    time.sleep(3)

    # Start frontend server
    print("🚀 Starting frontend server...")

    # Check if npm or yarn is available
    if (frontend_dir / "yarn.lock").exists():
        frontend_cmd = "yarn dev"
    else:
        frontend_cmd = "npm run dev"

    if sys.platform == "win32":
        frontend_process = subprocess.Popen(
            frontend_cmd,
            shell=True,
            cwd=frontend_dir
        )
    else:
        frontend_process = subprocess.Popen(
            frontend_cmd,
            shell=True,
            cwd=frontend_dir
        )

    print()
    print("=" * 50)
    print("  ✅ Both servers are starting!")
    print("  📡 Backend:  http://localhost:8001")
    print("  🌐 Frontend: http://localhost:4000")
    print("=" * 50)
    print()
    print("Press Ctrl+C to stop both servers...")
    print()

    try:
        # Wait for both processes
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping servers...")
        try:
            backend_process.terminate()
            frontend_process.terminate()
            time.sleep(1)
            if backend_process.poll() is None:
                backend_process.kill()
            if frontend_process.poll() is None:
                frontend_process.kill()
        except BaseException:
            pass
        print("✅ Servers stopped.")


if __name__ == "__main__":
    main()
