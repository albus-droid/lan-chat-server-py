# LAN Chat Server (Python)

A small TCP-based LAN chat server example focused on teaching/experimentation.

Features:
- single-file server: `main.py`
- broadcast server messages typed on stdin to all connected clients
- graceful shutdown via SIGINT/SIGTERM
- configurable host/port and worker pool size

Quick start

```bash
python3 main.py --host 0.0.0.0 --port 8080
```

Options:
- `--no-color` disable ANSI colors
- `--workers` maximum concurrent client handlers (default 8)

Notes

- This is a simple demo; consider using `asyncio` or proper framing for production.

Tests:
- Run tests with `python -m unittest discover -s tests` from the root