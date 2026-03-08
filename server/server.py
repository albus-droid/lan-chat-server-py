# server.py
from __future__ import annotations
import socket
# import threading
import asyncio
# from concurrent.futures import ThreadPoolExecutor
from typing import Set, Tuple
import logging
from collections import deque

from server import colors
from server.client import ClientSession
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
        # self.workers = workers

        self.sock: socket.socket | None = None
        self.clients: Set[ClientSession] = set()
        # self.clients_lock = threading.Lock()
        # self.stop_event = threading.Event()
        self.history: deque[str] = deque(maxlen=10)

    async def start(self) -> None:
        self.sock = socket_setup(self)
        self.sock.setblocking(False)
        logging.info(f"Server listening on {self.host}:{self.port}")

        loop = asyncio.get_running_loop()

        # threading.Thread(target=server_broadcast_loop, args=(self,), daemon=True).start()
        asyncio.create_task(server_broadcast_loop(self))
        
        # with ThreadPoolExecutor(max_workers=self.workers) as executor:
        # while not self.stop_event.is_set():
        while True:
            try:
                conn, addr = await loop.sock_accept(self.sock)
        #   except socket.timeout:
        #       continue
            except Exception:
                break

            # conn.settimeout(1.0)
            session = ClientSession(conn, addr)
            logging.info(f"Client info {session.conn}:{session.addr}")
            # with self.clients_lock:
            self.clients.add(session)

            # executor.submit(self.handle_client, session)
            asyncio.create_task(self.handle_client(session, loop))

        self.cleanup()

    def shutdown(self) -> None:
        logging.info("Shutting down server...")
        loop = asyncio.get_event_loop()
        # self.stop_event.set()
        try:
            if self.sock:
                self.sock.close()
        except Exception:
            pass
        pending = asyncio.all_tasks(loop)
        for task in pending:
            task.cancel()            
        loop.stop()

    async def handle_client(self, session : ClientSession, loop) -> None:

        conn = session.conn
        addr = session.addr

        logging.info(f"{colors.color('Connected by', colors.GREEN)} {addr}")
        await send_history(self, session)
        await loop.sock_sendall(session.conn, f"{colors.color('Welcome to the server!', colors.BLUE)}\n".encode())

        try:
            # while not self.stop_event.is_set():
            while True:
                # try:
                data = await loop.sock_recv(conn, 1024)
                # except socket.timeout:
                    # continue
                if not data:
                    break

                msg = data.decode(errors="replace").strip()
                if not msg:
                    continue

                if msg == "/end":
                    await send_to_conn(self, session, "Closing connection\n")
                    break

                logging.info(colors.color(f"{session.name}: {msg}", session.color))
                await broadcast_message(self, colors.color(f"{session.name}: {msg}\n", session.color), session)
                store_history(self, f"{session.name}: {msg}\n")
        
        finally:
            # with self.clients_lock:
            self.clients.discard(session)
            session.close()
            logging.info(f"{colors.color('Closing connection with', colors.RED)} {addr}")

    def cleanup(self) -> None:
        # with self.clients_lock:
        sessions = list(self.clients)
        self.clients.clear()
        
        for c in sessions:
            c.close()
