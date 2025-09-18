#!/usr/bin/env python3
"""
Enhanced server startup script with better error handling and port management
"""

import sys
import socket
import subprocess
import time
import webbrowser
from pathlib import Path

def check_port(port):
    """Check if a port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', port))
            return True
    except OSError:
        return False

def find_free_port(start_port=8000, max_attempts=10):
    """Find a free port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        if check_port(port):
            return port
    return None

def kill_process_on_port(port):
    """Kill any process running on the specified port (Windows)"""
    try:
        # Find process using the port
        result = subprocess.run(
            f'netstat -ano | findstr :{port}',
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if f':{port}' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        print(f"🔄 Killing process {pid} on port {port}")
                        subprocess.run(f'taskkill /PID {pid} /F', shell=True)
                        time.sleep(2)
                        return True
    except Exception as e:
        print(f"⚠️  Could not kill process on port {port}: {e}")
    
    return False

def main():
    print("🚀 Synthetic Data Generation Service - Server Startup")
    print("=" * 60)
    
    # Check if main.py exists
    if not Path("main.py").exists():
        print("❌ main.py not found. Please run this script from the project directory.")
        sys.exit(1)
    
    # Find a free port
    port = find_free_port()
    
    if port is None:
        print("❌ No free ports available in range 8000-8009")
        print("💡 Please close other services or try manually specifying a port")
        sys.exit(1)
    
    # If port 8000 is busy, try to free it
    if port != 8000:
        print(f"⚠️  Port 8000 is busy, trying to free it...")
        if kill_process_on_port(8000):
            port = 8000
            print(f"✅ Freed port 8000")
        else:
            print(f"⚠️  Could not free port 8000, using port {port}")
    
    print(f"🌐 Starting server on port {port}")
    print(f"📱 Web Interface: http://localhost:{port}")
    print(f"📚 API Documentation: http://localhost:{port}/docs")
    print(f"🔧 Alternative API Docs: http://localhost:{port}/redoc")
    print("\n" + "=" * 60)
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Start the server
    try:
        import uvicorn
        from main import app
        
        # Open browser after a short delay
        def open_browser():
            time.sleep(2)
            try:
                webbrowser.open(f'http://localhost:{port}')
                print(f"🌐 Opened browser to http://localhost:{port}")
            except Exception as e:
                print(f"⚠️  Could not open browser: {e}")
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Please install dependencies: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("💡 Check the error message above for details")

if __name__ == "__main__":
    main()
