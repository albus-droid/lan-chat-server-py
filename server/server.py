# server.py
from __future__ import annotations
import socket
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Set, Tuple
import logging
from collections import deque

import server.colors
from server.utils import (
    socket_setup,
    server_broadcast_loop,
    broadcast_message,
    send_to_conn,
    store_history,
    send_history
)


class Server:
    def __init__(self, host: str = "0.0.0.0", port: int = 8080, workers: int = 8):
        self.host = host
        self.port = port
        self.workers = workers

        self.sock: socket.socket | None = None
        self.clients: Set[ClientSession] = set()
        self.clients_lock = threading.Lock()
        self.stop_event = threading.Event()
        self.history: deque[str] = deque(maxlen=10)

    def start(self) -> None:
        self.sock = socket_setup(self)

        logging.info(f"Server listening on {self.host}:{self.port}")

        threading.Thread(target=server_broadcast_loop, args=(self,), daemon=True).start()

        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            while not self.stop_event.is_set():
                try:
                    conn, addr = self.sock.accept()
                except socket.timeout:
                    continue
                except Exception:
                    break

                conn.settimeout(1.0)
                session = ClientSession(conn, addr)
                with self.clients_lock:
                    self.clients.add(session)

                executor.submit(self.handle_client, session)

        self.cleanup()

    def shutdown(self) -> None:
        logging.info("Shutting down server...")
        self.stop_event.set()
        try:
            if self.sock:
                self.sock.close()
        except Exception:
            pass

    def handle_client(self, session : ClientSession) -> None:
        conn = session.conn
        addr = session.addr

        logging.info(f"{colors.color('Connected by', colors.GREEN)} {addr}")
        send_history(self, conn)
        conn.sendall(f"{colors.color('Welcome to the server!', colors.BLUE)}\n".encode())

        try:
            while not self.stop_event.is_set():
                try:
                    data = conn.recv(1024)
                except socket.timeout:
                    continue
                if not data:
                    break

                msg = data.decode(errors="replace").strip()
                if not msg:
                    continue

                if msg == "/end":
                    send_to_conn(self, conn, "Closing connection\n")
                    break
                logging.info(colors.color(f"{session.name}: {msg}", session.color))
                broadcast_message(self, colors.color(f"{session.name}: {msg}\n", session.color), conn)
                store_history(self, f"{session.name}: {msg}\n")
        finally:
            with self.clients_lock:
                self.clients.discard(session)
            try:
                conn.close()
            except Exception:
                pass
            logging.info(f"{colors.color('Closing connection with', colors.RED)} {addr}")

    def cleanup(self) -> None:
        with self.clients_lock:
            sessions = list(self.clients)
            self.sessions.clear()
        for c in sessions:
            c.close()