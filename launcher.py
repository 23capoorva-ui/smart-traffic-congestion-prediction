"""
NEXTRAFFX Intelligent Traffic Management System - Application Launcher.
Automatically discovers available ports (handling Windows WinError 10013 port reservation/locks),
opens the default web browser, and runs the Streamlit application reliably.
"""

import os
import sys
import time
import socket
import webbrowser
import subprocess

def find_available_port(preferred_ports=(8501, 8502, 8503, 8504, 8505, 8080)):
    """Finds the first available port that can be bound on 127.0.0.1."""
    for p in preferred_ports:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(('127.0.0.1', p))
            s.close()
            return p
        except Exception:
            continue
    return 8502

def main():
    print("=" * 68)
    print("      NEXTRAFFX - INTELLIGENT TRAFFIC MANAGEMENT SYSTEM")
    print("              Multi-City Production Architecture")
    print("=" * 68)
    print()

    target_port = find_available_port()
    print(f"[*] Detected available network port: {target_port}")
    target_url = f"http://localhost:{target_port}"
    print(f"[*] Application URL: {target_url}")
    print()
    print("[*] Launching Streamlit web engine...")
    print("[*] Press Ctrl+C in this terminal window to stop the server.")
    print("-" * 68)

    # Launch browser after a brief delay
    def open_browser():
        time.sleep(1.8)
        webbrowser.open(target_url)

    import threading
    b_thread = threading.Thread(target=open_browser, daemon=True)
    b_thread.start()

    cmd = [
        sys.executable,
        "-m", "streamlit", "run", "app.py",
        "--server.port", str(target_port),
        "--server.headless", "true"
    ]

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n[*] Server stopped by user.")

if __name__ == "__main__":
    main()
