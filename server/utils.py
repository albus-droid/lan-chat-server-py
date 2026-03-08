import socket
import sys
import asyncio
from typing import Iterable

from . import colors
from server.client import ClientSession

def socket_setup(server) -> socket.socket:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((server.host, server.port))
    s.listen()
    # s.settimeout(1.0)
    return s


async def send_to_conn(server, session: ClientSession, msg: str) -> None:
    loop = asyncio.get_running_loop()
    try:
        # session.conn.sendall(msg.encode())
        await loop.sock_sendall(session.conn, msg.encode())
    except Exception:
        try:
            session.close()
        except Exception:
            pass
        # with server.clients_lock:
        server.clients.discard(session)


async def broadcast_message(server, msg: str, sender: ClientSession | None = None) -> None:
    # with server.clients_lock:
    snapshot = list(server.clients)
    loop = asyncio.get_running_loop()

    dead = []
    for s in snapshot:
        if sender is not None and s is sender:
            continue
        try:
            # s.conn.sendall(msg.encode())
            await loop.sock_sendall(s.conn, msg.encode())
        except Exception:
            s.close()
            dead.append(s)

    if dead:
        # with server.clients_lock:
        for s in dead:
            server.clients.discard(s)        

def stdin_readable(queue):
    line = sys.stdin.readline()
    if not line:
        return
    text = line.strip()
    if not text:
        return
    queue.put_nowait(text)

async def server_broadcast_loop(server) -> None:
    # while not server.stop_event.is_set():
    loop = asyncio.get_running_loop()
    queue = asyncio.Queue()

    loop.add_reader(sys.stdin.fileno(), stdin_readable, queue)

    try:
        while True:
            # line = sys.stdin.readline()
            text = await queue.get()
            await broadcast_message(server, f"{colors.color('Server: ', colors.YELLOW)} {text}\n")
            store_history(server, f"Server: {text}\n")
    finally:
        loop.remove_reader(sys.stdin.fileno())

def store_history(server, msg: str) -> None:
    server.history.append(msg)

async def send_history(server, session: ClientSession) -> None:
    if not server.history:
        return
    for msg in server.history:
        send_to_conn(server, session, msg)
