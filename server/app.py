"""FastAPI server with Socket.IO and Nicegui integration."""

import os
from pathlib import Path
from typing import List

import socketio
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from events.socketio_handlers import TerminalHandler

# Create FastAPI app
app = FastAPI(title="Claude Web Terminal")

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
)

# Create Socket.IO ASGI app
sio_app = socketio.ASGIApp(sio, other_asgi_app=app)

# Initialize terminal handler
terminal_handler = TerminalHandler(sio)


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse({"status": "ok"})


@app.get("/api/workspaces")
async def list_workspaces() -> List[dict]:
    """List available workspaces (directories in $HOME).

    Returns:
        List of workspace info dicts
    """
    home = Path.home()
    workspaces = []

    # Add home directory itself
    workspaces.append({
        "name": "~",
        "path": str(home),
        "is_git": (home / ".git").exists(),
    })

    # Common workspace directories
    common_dirs = ["Workspace", "workspace", "Projects", "projects", "dev", "code"]

    for dir_name in common_dirs:
        dir_path = home / dir_name
        if dir_path.is_dir():
            # Add the directory itself
            workspaces.append({
                "name": f"~/{dir_name}",
                "path": str(dir_path),
                "is_git": (dir_path / ".git").exists(),
            })
            # Add subdirectories
            try:
                for sub in sorted(dir_path.iterdir()):
                    if sub.is_dir() and not sub.name.startswith("."):
                        workspaces.append({
                            "name": f"~/{dir_name}/{sub.name}",
                            "path": str(sub),
                            "is_git": (sub / ".git").exists(),
                        })
            except PermissionError:
                pass

    return workspaces


def get_asgi_app():
    """Get the ASGI application for uvicorn.

    Returns:
        Socket.IO ASGI app wrapping FastAPI
    """
    return sio_app
