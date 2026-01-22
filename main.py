#!/usr/bin/env python3
"""Claude Web Terminal - Main entry point."""

import argparse
import os
import signal
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

DEFAULT_PORT = 6388
PID_FILE = Path.home() / ".claude-web.pid"


def get_pid() -> int | None:
    """Get running server PID from file.

    Returns:
        PID if file exists and process is running, None otherwise
    """
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            # Check if process is running
            os.kill(pid, 0)
            return pid
        except (ValueError, ProcessLookupError, PermissionError):
            PID_FILE.unlink(missing_ok=True)
    return None


def save_pid():
    """Save current process PID to file."""
    PID_FILE.write_text(str(os.getpid()))


def remove_pid():
    """Remove PID file."""
    PID_FILE.unlink(missing_ok=True)


def start_server(port: int):
    """Start the web server.

    Args:
        port: Port number to listen on
    """
    # Check if already running
    existing_pid = get_pid()
    if existing_pid:
        print(f"Server already running (PID: {existing_pid})")
        print(f"Stop it first with: python {__file__} stop")
        sys.exit(1)

    # Import here to avoid loading heavy modules for stop command
    import socketio
    import uvicorn
    from nicegui import app, ui

    from events.socketio_handlers import TerminalHandler
    from ui.components.terminal import Terminal

    # Create Socket.IO server
    sio = socketio.AsyncServer(
        async_mode="asgi",
        cors_allowed_origins="*",
    )

    # Initialize terminal handler
    terminal_handler = TerminalHandler(sio)

    # Mount Socket.IO to Nicegui's FastAPI app
    sio_asgi = socketio.ASGIApp(sio)
    app.mount("/socket.io", sio_asgi)

    # API endpoint for workspaces
    from fastapi import Response
    import json

    @app.get("/api/workspaces")
    def get_workspaces_api():
        """Return list of workspaces as JSON."""
        from ui.components.workspace_selector import get_workspaces
        workspaces = get_workspaces()
        return Response(
            content=json.dumps(workspaces),
            media_type="application/json"
        )

    # Main page
    @ui.page("/")
    def index():
        """Main page with terminal."""
        ui.dark_mode().enable()

        # Remove default padding and ensure full height
        ui.query('body').classes('p-0 m-0').style('overflow: hidden')
        ui.query('.nicegui-content').classes('p-0').style('height: 100vh; overflow: hidden')

        # Terminal takes full screen
        terminal = Terminal()
        terminal.render()

    # Save PID and setup cleanup
    save_pid()

    def cleanup(signum=None, frame=None):
        remove_pid()
        sys.exit(0)

    signal.signal(signal.SIGTERM, cleanup)
    signal.signal(signal.SIGINT, cleanup)

    print(f"Starting Claude Web Terminal on http://localhost:{port}")
    print(f"PID: {os.getpid()}")
    print("Press Ctrl+C to stop")

    try:
        ui.run(
            host="0.0.0.0",
            port=port,
            title="Claude Web Terminal",
            favicon="🤖",
            show=False,
            reload=False,
        )
    finally:
        remove_pid()


def stop_server():
    """Stop the running server."""
    pid = get_pid()
    if pid:
        print(f"Stopping server (PID: {pid})...")
        try:
            os.kill(pid, signal.SIGTERM)
            print("Server stopped")
        except ProcessLookupError:
            print("Server process not found")
        finally:
            remove_pid()
    else:
        print("No server running")


def status():
    """Show server status."""
    pid = get_pid()
    if pid:
        print(f"Server is running (PID: {pid})")
    else:
        print("Server is not running")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Claude Web Terminal - Web-based Claude terminal service"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Start command
    start_parser = subparsers.add_parser("start", help="Start the server")
    start_parser.add_argument(
        "port",
        nargs="?",
        type=int,
        default=DEFAULT_PORT,
        help=f"Port number (default: {DEFAULT_PORT})",
    )

    # Stop command
    subparsers.add_parser("stop", help="Stop the server")

    # Status command
    subparsers.add_parser("status", help="Show server status")

    args = parser.parse_args()

    if args.command == "start":
        start_server(args.port)
    elif args.command == "stop":
        stop_server()
    elif args.command == "status":
        status()
    else:
        # Default to start if no command
        parser.print_help()


if __name__ == "__main__":
    main()
