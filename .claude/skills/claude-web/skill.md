---
name: claude-web
description: Start or stop the Claude Web Terminal server.
---

# Claude Web Terminal

Manages the web-based Claude terminal service.

## Usage

```
/claude-web start [port]  # Start server (default port: 6388)
/claude-web stop          # Stop server
```

## Workflow

### Argument Parsing

Extract command and port from user input:
- `start` or no args → Start server
- `start 8080` → Start server on port 8080
- `stop` → Stop server

### Start Command

```bash
cd "$CLAUDE_PROJECT_DIR"
uv run python main.py start [port]
# or
source .venv/bin/activate && python main.py start [port]
```

- Default port: 6388
- PID file: ~/.claude-web.pid
- Server URL: http://localhost:[port]

### Stop Command

```bash
cd "$CLAUDE_PROJECT_DIR"
uv run python main.py stop
# or
source .venv/bin/activate && python main.py stop
```

## Install Dependencies (First Time)

### Using uv (Recommended)

```bash
cd "$CLAUDE_PROJECT_DIR"
uv venv
uv pip install -e .
```

### Using pip

```bash
cd "$CLAUDE_PROJECT_DIR"
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Examples

### Start Server
```
User: /claude-web start
→ Server starts at http://localhost:6388
```

### Start on Custom Port
```
User: /claude-web start 8080
→ Server starts at http://localhost:8080
```

### Stop Server
```
User: /claude-web stop
→ Running server stops
```
