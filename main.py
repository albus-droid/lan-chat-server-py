#!/usr/bin/env python3
import socket
import threading

HOST = "0.0.0.0"

def end_connection(conn, addr):
    print("Closing connection with", addr)
    conn.close()
    
def handle_client(conn, addr):
       print("Connected by", addr)
       while True:
           msg = conn.recv(1024)
           if not msg or msg.decode().strip() == "/end":
               end_connection(conn, addr)
               break
           print(addr, ":", msg.decode())

def socket_run():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, 8080))
    s.listen()
    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()
        

if __name__ == "__main__":
     socket_run()
