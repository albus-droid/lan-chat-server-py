#!/usr/bin/env python3
import socket

HOST = "0.0.0.0"

def end_connection(conn, addr):
    print("Closing connection with", addr)
    conn.close()
    
def socket_run():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, 8080))
    s.listen()
    while True:
        conn, addr = s.accept()
        print("Connected by", addr)
        while True:
            msg = conn.recv(1024)
            if msg.decode().strip() == "/end":
                end_connection(conn, addr)
                break
            print(addr, ":", msg.decode())

if __name__ == "__main__":
    socket_run()
