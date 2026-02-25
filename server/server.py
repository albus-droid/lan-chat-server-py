# server.py
from __future__ import annotations
import socket
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Set, Tuple
import logging
import colors
from collections import deque

from utils import (
    socket_setup,
    server_broadcast_loop,
    broadcast_message,
    send_to_conn,
)


class Server:
    def __init__(self, host: str = "0.0.0.0", port: int = 8080, workers: int = 8):
        self.host = host
        self.port = port
        self.workers = workers

        self.sock: socket.socket | None = None
        self.clients: Set[socket.socket] = set()
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
                with self.clients_lock:
                    self.clients.add(conn)

                executor.submit(self.handle_client, conn, addr)

        self.cleanup()

    def shutdown(self) -> None:
        logging.info("Shutting down server...")
        self.stop_event.set()
        try:
            if self.sock:
                self.sock.close()
        except Exception:
            pass

    def handle_client(self, conn: socket.socket, addr: Tuple[str, int]) -> None:
        logging.info(f"{colors.color('Connected by', colors.GREEN)} {addr}")
        try:
            while not self.stop_event.is_set():
                try:
                    send_history(self, conn)
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

                logging.info(f"{addr}: {msg}")
                broadcast_message(self, f"{addr}: {msg}\n")
                store_history(self, f"{addr}: {msg}\n")

        finally:
            with self.clients_lock:
                self.clients.discard(conn)
            try:
                conn.close()
            except Exception:
                pass
            logging.info(f"{colors.color('Closing connection with', colors.RED)} {addr}")

    def cleanup(self) -> None:
        try:
            if self.sock:
                self.sock.close()
        except Exception:
            pass
        with self.clients_lock:
            for c in list(self.clients):
                try:
                    c.close()
                except Exception:
                    pass
            self.clients.clear()