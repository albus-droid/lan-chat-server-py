import socket
import sys
from typing import Iterable


def socket_setup(server) -> socket.socket:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((server.host, server.port))
    s.listen()
    s.settimeout(1.0)
    return s


def send_to_conn(server, conn: socket.socket, msg: str) -> None:
    try:
        conn.sendall(msg.encode())
    except Exception:
        try:
            conn.close()
        except Exception:
            pass
        with server.clients_lock:
            server.clients.discard(conn)


def broadcast_message(server, msg: str) -> None:
    with server.clients_lock:
        for c in list(server.clients):
            try:
                c.sendall(msg.encode())
            except Exception:
                try:
                    c.close()
                except Exception:
                    pass
                server.clients.discard(c)


def server_broadcast_loop(server) -> None:
    while not server.stop_event.is_set():
        line = sys.stdin.readline()
        if not line:
            break
        text = line.strip()
        if not text:
            continue
        broadcast_message(server, f"Server: {text}\n")

def store_history(server, msg: str) -> None:
    server.history.append(msg)

def send_history(server, conn: socket.socket) -> None:
    logging.info(f"Sending history to {conn.getpeername()}")
    if not server.history:
        return
    for msg in server.history:
        send_to_conn(server, conn, msg)