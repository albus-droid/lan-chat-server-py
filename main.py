#!/usr/bin/env python3
import socket

HOST = "0.0.0.0"

def socket_run():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, 8080))
    s.listen()
    while True:
        conn, addr = s.accept()
        print("Connected by", addr)
        msg = conn.recv(1024)
        print(msg)

if __name__ == "__main__":
    socket_run()
    
