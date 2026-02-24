#!/usr/bin/env python3
"""Small TCP LAN chat server with improved structure and logging.

Features:
- command line args (host, port, no-color)
- logging instead of prints
- ThreadPoolExecutor for clients
- single stdin thread to broadcast server messages
- graceful shutdown handling
"""

from __future__ import annotations

import argparse
import logging
import socket
import signal
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Set

import colors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="LAN chat server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    parser.add_argument("--workers", type=int, default=8, help="Max client handler threads")
    return parser.parse_args()


clients: Set[socket.socket] = set()
clients_lock = threading.Lock()
stop_event = threading.Event()


def send_safe(conn: socket.socket, msg: str) -> None:
    try:
        conn.sendall(msg.encode())
    except Exception:
        with clients_lock:
            if conn in clients:
                clients.remove(conn)
        try:
            conn.close()
        except Exception:
            pass


def handle_client(conn: socket.socket, addr: tuple) -> None:
    logging.info("%s %s", colors.color("Connected by", colors.GREEN), addr)
    try:
        while not stop_event.is_set():
            try:
                data = conn.recv(1024)
            except socket.timeout:
                continue
            except Exception:
                break
            if not data:
                break
            msg = data.decode(errors="replace").strip()
            if not msg:
                continue
            if msg == "/end":
                send_safe(conn, "Closing Connection")
                break
            logging.info("%s: %s", addr, msg)
            send_safe(conn, "Message received by the server\n")
    finally:
        with clients_lock:
            if conn in clients:
                clients.remove(conn)
        try:
            conn.close()
        except Exception:
            pass
        logging.info("%s %s", colors.color("Closing connection with", colors.RED), addr)


def stdin_thread() -> None:
    """Read lines from server stdin and broadcast to all connected clients."""
    while not stop_event.is_set():
        line = sys.stdin.readline()
        if not line:
            break
        text = line.strip()
        if not text:
            continue
        msg = f"Server: {text}\n"
        with clients_lock:
            conns = list(clients)
        for c in conns:
            send_safe(c, msg)


def start_server(host: str, port: int, workers: int) -> None:
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((host, port))
    srv.listen()
    srv.settimeout(1.0)

    logging.info("Server listening on %s:%d", host, port)

    with ThreadPoolExecutor(max_workers=workers) as exe:
        while not stop_event.is_set():
            try:
                conn, addr = srv.accept()
            except socket.timeout:
                continue
            except Exception:
                break
            conn.settimeout(1.0)
            with clients_lock:
                clients.add(conn)
            exe.submit(handle_client, conn, addr)

    # cleanup
    try:
        srv.close()
    except Exception:
        pass
    with clients_lock:
        for c in list(clients):
            try:
                c.close()
            except Exception:
                pass
        clients.clear()


def shutdown(signum, frame) -> None:  # pragma: no cover - signal handler
    logging.info("Shutting down server...")
    stop_event.set()


def main() -> None:
    args = parse_args()
    log_level = logging.INFO
    logging.basicConfig(level=log_level, format="%(asctime)s %(levelname)s: %(message)s")

    if args.no_color:
        # simple way to disable colors: replace color codes with identity
        colors.RESET = colors.BOLD = colors.RED = colors.GREEN = colors.YELLOW = ""

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # start stdin reader
    t = threading.Thread(target=stdin_thread, daemon=True)
    t.start()

    try:
        start_server(args.host, args.port, args.workers)
    except PermissionError:
        logging.error("Permission denied binding to %s:%d", args.host, args.port)
        sys.exit(1)
    except OSError as e:
        logging.error("OS error: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
