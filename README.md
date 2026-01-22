# Claude Web Terminal

Web-based Claude terminal service using Nicegui + xterm.js frontend and FastAPI + asyncssh + Socket.IO backend.

## Features

- **Workspace Selection**: Searchable dropdown with project directories under $HOME
- **Multi-tab Terminal**: Split panes (horizontal/vertical), multiple tabs per pane
- **SSH Connection**: Connect to localhost via SSH (pubkey preferred, password optional)
- **Real-time Communication**: Socket.IO for input/output streaming
- **Bell Sound**: Audio notification support for terminal bell
- **Auto-close**: Terminal closes when Claude exits

## Installation

```bash
# Clone repository
git clone https://github.com/dnomad-sy/claude-web-terminal.git
cd claude-web-terminal

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .
```

## Usage

### Start Server

```bash
python main.py start [port]
```

- Default port: 6388
- Access: http://localhost:6388

### Stop Server

```bash
python main.py stop
```

### Check Status

```bash
python main.py status
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Cmd+T` | New tab |
| `Cmd+W` | Close tab |
| `Cmd+D` | Split vertical |
| `Shift+Cmd+D` | Split horizontal |
| `Cmd+[` | Previous tab |
| `Cmd+]` | Next tab |

## Architecture

```
claude-web-terminal/
├── main.py                    # Entry point (CLI)
├── pyproject.toml             # Dependencies
├── events/
│   └── socketio_handlers.py   # Socket.IO event handlers
├── ssh/
│   └── session.py             # asyncssh session management
└── ui/
    └── components/
        ├── terminal.py        # xterm.js terminal component
        └── workspace_selector.py  # Workspace selection UI
```

## Requirements

- Python 3.10+
- SSH server running on localhost
- SSH key authentication configured (or use password)

## Dependencies

- nicegui
- python-socketio
- asyncssh
- fastapi
- uvicorn

## License

MIT License
