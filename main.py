"""
Ca Mau Fertilizer Classification & Tracking System.
Modern Web-based AI Vision System.

Usage:
  python main.py              # Start server & auto-open web dashboard in browser
  python main.py --no-browser # Start server only (headless)
  python main.py --server     # Listen on 0.0.0.0 for LAN access (tablets, phones, other PCs)
"""

import argparse
import os
import sys
import threading
import time
import urllib.request
import webbrowser

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import uvicorn
from src.web.app import app

HOST = "127.0.0.1"
PORT = 8000


def wait_for_server(url, timeout=15):
    """Wait until backend server responds with 200 OK."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return True
        except Exception:
            time.sleep(0.3)
    return False


def main():
    parser = argparse.ArgumentParser(description="Ca Mau Fertilizer AI Vision Web Dashboard")
    parser.add_argument("--host", default=HOST, help="Host address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=PORT, help="Port (default: 8000)")
    parser.add_argument("--no-browser", action="store_true", help="Do not open web browser automatically")
    parser.add_argument("--server", action="store_true", help="Listen on 0.0.0.0 for LAN access")
    args = parser.parse_args()

    target_host = "0.0.0.0" if args.server else args.host
    url = f"http://{args.host}:{args.port}"

    print("=" * 75)
    print("   HE THONG NHAN DIEN, PHAN LOAI & DEM BAO PHAN BON CA MAU (WEB AI)")
    print(f"   Dashboard Web: {url}")
    print("=" * 75)

    if not args.no_browser:
        # Start server in daemon thread, then open browser
        server_thread = threading.Thread(
            target=lambda: uvicorn.run(app, host=target_host, port=args.port, log_level="warning"),
            daemon=True,
        )
        server_thread.start()

        print("[SYSTEM] Dang khoi dong may chu FastAPI va model AI...")
        if wait_for_server(url):
            print(f"[READY] Dang mo giao dien tren trinh duyet ({url})...")
            webbrowser.open(url)
        else:
            print(f"[READY] May chu dang chay tai: {url}")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[STOP] Da dung he thong.")
    else:
        # Run directly on main thread
        uvicorn.run(app, host=target_host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
