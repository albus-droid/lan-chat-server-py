import socket
import sys
from typing import Iterable
from . import colors
from server.client import ClientSession

def socket_setup(server) -> socket.socket:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((server.host, server.port))
    s.listen()
    s.settimeout(1.0)
    return s


def send_to_conn(server, session: ClientSession, msg: str) -> None:
    try:
        session.conn.sendall(msg.encode())
    except Exception:
        try:
            session.close()
        except Exception:
            pass
        with server.clients_lock:
            server.clients.discard(session)


def broadcast_message(server, msg: str, sender: ClientSession | None = None) -> None:
    with server.clients_lock:
        snapshot = list(server.clients)

    dead = []
    for s in snapshot:
        if sender is not None and s is sender:
            continue
        try:
            s.conn.sendall(msg.encode())
        except Exception:
            s.close()
            dead.append(s)

    if dead:
        with server.clients_lock:
            for s in dead:
                server.clients.discard(s)        


def server_broadcast_loop(server) -> None:
    while not server.stop_event.is_set():
        line = sys.stdin.readline()
        if not line:
            break
        text = line.strip()
        if not text:
            continue
        broadcast_message(server, f"{colors.color('Server: ', colors.YELLOW)} {text}\n")
        store_history(server, f"Server: {text}\n")

def store_history(server, msg: str) -> None:
    server.history.append(msg)

def send_history(server, conn: socket.socket) -> None:
    if not server.history:
        return
    for msg in server.history:
        send_to_conn(server, conn, msg)
