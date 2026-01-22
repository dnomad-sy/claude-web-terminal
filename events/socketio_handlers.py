"""Socket.IO event handlers for terminal communication."""

import asyncio
from typing import Dict

import socketio

from ssh.session import SSHSession


class TerminalHandler:
    """Handles Socket.IO events for terminal sessions."""

    def __init__(self, sio: socketio.AsyncServer):
        """Initialize handler with Socket.IO server.

        Args:
            sio: AsyncServer instance
        """
        self.sio = sio
        # sessions[sid][tab_id] = SSHSession
        self.sessions: Dict[str, Dict[str, SSHSession]] = {}
        self._register_handlers()

    def _register_handlers(self):
        """Register all Socket.IO event handlers."""

        @self.sio.event
        async def connect(sid, environ):
            """Handle client connection."""
            print(f"[SocketIO] Client connected: {sid}")
            self.sessions[sid] = {}

        @self.sio.event
        async def disconnect(sid):
            """Handle client disconnection."""
            print(f"[SocketIO] Client disconnected: {sid}")
            await self._cleanup_all_sessions(sid)

        @self.sio.event
        async def start_session(sid, data):
            """Start SSH session for client.

            Args:
                sid: Client session ID
                data: Dict with workspace, tab_id, and optional password
            """
            workspace = data.get("workspace", "")
            tab_id = data.get("tab_id", "default")
            password = data.get("password")
            cols = data.get("cols", 120)
            rows = data.get("rows", 40)

            if not workspace:
                await self.sio.emit(
                    "terminal_error",
                    {"tab_id": tab_id, "message": "Workspace is required"},
                    to=sid,
                )
                return

            # Create output callback for this session
            async def send_output(text: str):
                await self.sio.emit("terminal_output", {"tab_id": tab_id, "data": text}, to=sid)

            def output_callback(text: str):
                asyncio.create_task(send_output(text))

            # Create close callback
            async def send_close():
                await self.sio.emit("session_closed", {"tab_id": tab_id}, to=sid)

            def close_callback():
                asyncio.create_task(send_close())
                # Clean up session
                if sid in self.sessions and tab_id in self.sessions[sid]:
                    del self.sessions[sid][tab_id]

            # Create and connect SSH session
            session = SSHSession(on_output=output_callback, on_close=close_callback)
            success = await session.connect(
                workspace=workspace,
                password=password,
                cols=cols,
                rows=rows,
            )

            if success:
                if sid not in self.sessions:
                    self.sessions[sid] = {}
                self.sessions[sid][tab_id] = session
                await self.sio.emit("session_started", {"tab_id": tab_id, "workspace": workspace}, to=sid)
            else:
                await self.sio.emit(
                    "terminal_error",
                    {"tab_id": tab_id, "message": "Failed to connect SSH session"},
                    to=sid,
                )

        @self.sio.event
        async def terminal_input(sid, data):
            """Handle terminal input from client.

            Args:
                sid: Client session ID
                data: Dict with tab_id and input string
            """
            tab_id = data.get("tab_id", "default")
            if sid in self.sessions and tab_id in self.sessions[sid]:
                session = self.sessions[sid][tab_id]
                if session.is_connected:
                    input_data = data.get("data", "")
                    await session.send_input(input_data)

        @self.sio.event
        async def terminal_resize(sid, data):
            """Handle terminal resize.

            Args:
                sid: Client session ID
                data: Dict with tab_id, cols and rows
            """
            tab_id = data.get("tab_id", "default")
            if sid in self.sessions and tab_id in self.sessions[sid]:
                session = self.sessions[sid][tab_id]
                if session.is_connected:
                    cols = data.get("cols", 120)
                    rows = data.get("rows", 40)
                    await session.resize(cols, rows)

        @self.sio.event
        async def stop_session(sid, data=None):
            """Stop SSH session for client.

            Args:
                sid: Client session ID
                data: Dict with tab_id
            """
            tab_id = data.get("tab_id", "default") if data else "default"
            await self._cleanup_session(sid, tab_id)
            await self.sio.emit("session_stopped", {"tab_id": tab_id}, to=sid)

    async def _cleanup_session(self, sid: str, tab_id: str):
        """Clean up SSH session for client.

        Args:
            sid: Client session ID
            tab_id: Tab identifier
        """
        if sid in self.sessions and tab_id in self.sessions[sid]:
            session = self.sessions[sid].pop(tab_id)
            # Clear on_close to prevent duplicate session_closed event
            session.on_close = None
            await session.disconnect()

    async def _cleanup_all_sessions(self, sid: str):
        """Clean up all SSH sessions for client.

        Args:
            sid: Client session ID
        """
        if sid in self.sessions:
            for tab_id, session in list(self.sessions[sid].items()):
                await session.disconnect()
            del self.sessions[sid]
