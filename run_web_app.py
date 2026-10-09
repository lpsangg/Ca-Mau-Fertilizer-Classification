"""
Desktop & Web Application Launcher for Ca Mau Fertilizer Classification System.
Runs the FastAPI Backend & opens a sleek Modern Desktop Window using PyWebView (Edge WebView2).

Usage:
  python run_web_app.py             # Launch as Native Desktop Application
  python run_web_app.py --browser   # Launch in standard Web Browser (Chrome/Edge)
  python run_web_app.py --server    # Launch as headless Network Server for LAN tablets/PCs
"""

import argparse
import os
import sys
import threading
import time
import urllib.request
import webbrowser

# Preload torch on Windows to avoid DLL conflicts
try:
    import torch
except ImportError:
    pass

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import uvicorn
from src.web.app import app

HOST = "127.0.0.1"
PORT = 8000
APP_URL = f"http://{HOST}:{PORT}"


def start_uvicorn_server(host=HOST, port=PORT):
    """Run Uvicorn ASGI server."""
    uvicorn.run(app, host=host, port=port, log_level="warning")


def wait_for_server(url, timeout=15):
    """Poll URL until server responds with 200 OK."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return True
        except Exception:
            time.sleep(0.3)
    return False


def launch_desktop_window():
    """Launch sleek desktop window using pywebview."""
    try:
        import webview

        print(f"[DESKTOP] Initializing High-Tech AI Dashboard Desktop Window...")
        window = webview.create_window(
            title="Hệ Thống Giám Sát & Đếm Phân Bón Cà Mau (PVCFC Vision AI)",
            url=APP_URL,
            width=1400,
            height=880,
            min_size=(1024, 680),
            background_color="#0A0E17",
            text_select=False,
            zoomable=True,
        )
        webview.start(debug=False)
    except Exception as e:
        print(f"[WARN] PyWebView window could not start ({e}). Falling back to Web Browser...")
        webbrowser.open(APP_URL)
        # Keep main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass


def main():
    parser = argparse.ArgumentParser(description="Ca Mau Fertilizer Modern AI Dashboard Launcher")
    parser.add_argument("--browser", action="store_true", help="Open in standard browser instead of desktop window")
    parser.add_argument("--server", action="store_true", help="Run as LAN server accessible from any device")
    parser.add_argument("--host", default=HOST, help="Host address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=PORT, help="Port (default: 8000)")
    args = parser.parse_args()

    target_host = "0.0.0.0" if args.server else args.host
    target_url = f"http://{args.host}:{args.port}"

    print("=" * 72)
    print("   HE THONG PHAN LOAI & DEM BAO PHAN BON CA MAU (MODERN WEB EDITION)")
    print(f"   Server: http://{target_host}:{args.port}")
    print("=" * 72)

    # Start FastAPI in background thread
    server_thread = threading.Thread(
        target=start_uvicorn_server,
        kwargs={"host": target_host, "port": args.port},
        daemon=True,
    )
    server_thread.start()

    print("[SYSTEM] Waiting for FastAPI server to initialize...")
    if not wait_for_server(target_url):
        print("[ERROR] FastAPI server failed to start within timeout.")
        sys.exit(1)

    print(f"[READY] Backend server online at {target_url}!")

    if args.server:
        print("[INFO] Server is running in LAN mode. Press Ctrl+C to exit.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[STOP] Shutting down...")
    elif args.browser:
        print(f"[BROWSER] Opening default web browser at {target_url}...")
        webbrowser.open(target_url)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[STOP] Shutting down...")
    else:
        # Default: Launch native Desktop window via pywebview
        launch_desktop_window()


if __name__ == "__main__":
    main()
