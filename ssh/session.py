"""SSH session management using asyncssh."""

import asyncio
import os
from typing import Callable, Optional

import asyncssh


class SSHSession:
    """Manages SSH connection to localhost with PTY support."""

    def __init__(self, on_output: Callable[[str], None], on_close: Optional[Callable[[], None]] = None):
        """Initialize SSH session.

        Args:
            on_output: Callback function to handle terminal output
            on_close: Callback function when session closes
        """
        self.on_output = on_output
        self.on_close = on_close
        self.conn: Optional[asyncssh.SSHClientConnection] = None
        self.process: Optional[asyncssh.SSHClientProcess] = None
        self._running = False
        self._output_started = False  # Flag to filter initial output

    async def connect(
        self,
        workspace: str,
        password: Optional[str] = None,
        term_type: str = "xterm-256color",
        cols: int = 120,
        rows: int = 40,
    ) -> bool:
        """Connect to localhost via SSH and start a PTY session.

        Args:
            workspace: Working directory to start in
            password: Optional password (uses pubkey if None)
            term_type: Terminal type for PTY
            cols: Terminal columns
            rows: Terminal rows

        Returns:
            True if connection successful
        """
        try:
            username = os.environ.get("USER", os.getlogin())
            home = os.path.expanduser("~")

            # Resolve workspace path
            if not os.path.isabs(workspace):
                workspace = os.path.join(home, workspace)

            # Connection options - prefer pubkey, fallback to password
            connect_kwargs = {
                "host": "localhost",
                "username": username,
                "known_hosts": None,  # Skip host key verification for localhost
            }

            if password:
                connect_kwargs["password"] = password
            else:
                # Try to use default SSH keys
                key_paths = [
                    os.path.join(home, ".ssh", "id_rsa"),
                    os.path.join(home, ".ssh", "id_ed25519"),
                    os.path.join(home, ".ssh", "id_ecdsa"),
                ]
                client_keys = [k for k in key_paths if os.path.exists(k)]
                if client_keys:
                    connect_kwargs["client_keys"] = client_keys

            self.conn = await asyncssh.connect(**connect_kwargs)

            # Start interactive shell with PTY
            self.process = await self.conn.create_process(
                term_type=term_type,
                term_size=(cols, rows),
                encoding=None,  # Binary mode for proper terminal handling
            )

            self._running = True
            self._output_started = False
            self._workspace = workspace

            # Start reading output
            asyncio.create_task(self._read_output())

            # Wait for shell to initialize, then cd and run claude
            # Using exec so that when claude exits, the shell exits too
            await asyncio.sleep(0.5)
            await self.send_input(f'cd "{workspace}" && clear && exec claude\n')

            return True

        except Exception as e:
            self.on_output(f"\r\n[SSH Error] {e}\r\n")
            return False

    async def _read_output(self):
        """Read output from SSH process and send to callback."""
        try:
            while self._running and self.process:
                data = await self.process.stdout.read(4096)
                if not data:
                    break
                # Decode output
                try:
                    text = data.decode("utf-8", errors="replace")
                except:
                    text = str(data)

                # Always output - filtering removed for reliability
                self.on_output(text)
        except Exception as e:
            if self._running:
                self.on_output(f"\r\n[Read Error] {e}\r\n")
        finally:
            self._running = False
            # Notify session closed
            if self.on_close:
                self.on_close()

    async def send_input(self, data: str):
        """Send input to SSH process.

        Args:
            data: Input string to send
        """
        if self.process and self._running:
            try:
                self.process.stdin.write(data.encode("utf-8"))
            except Exception as e:
                self.on_output(f"\r\n[Write Error] {e}\r\n")

    async def resize(self, cols: int, rows: int):
        """Resize terminal.

        Args:
            cols: New column count
            rows: New row count
        """
        if self.process and self._running:
            try:
                self.process.change_terminal_size(cols, rows)
            except Exception:
                pass  # Ignore resize errors

    async def disconnect(self):
        """Close SSH connection."""
        self._running = False
        if self.process:
            try:
                self.process.close()
                await self.process.wait_closed()
            except Exception:
                pass
            self.process = None
        if self.conn:
            try:
                self.conn.close()
                await self.conn.wait_closed()
            except Exception:
                pass
            self.conn = None

    @property
    def is_connected(self) -> bool:
        """Check if SSH session is active."""
        return self._running and self.process is not None
