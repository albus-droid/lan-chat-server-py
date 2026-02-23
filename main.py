#!/usr/bin/env python3
import socket
import threading
import sys
import colors 

HOST = "0.0.0.0"
PORT = 8080

def server_respond(conn, msg):
    conn.sendall(msg.encode())
    
def end_connection(conn, addr):
    print(colors.color("Closing connection with", colors.RED), addr)
    server_respond(conn, "Closing Connection")
    conn.close()

def server_client_msg(conn):
    line = sys.stdin.readline() 
    if line.strip():
       conn.sendall(("Server: "+ line).encode())

def handle_client(conn, addr):
       print(colors.color("Connected by", colors.GREEN), addr)
       while True:
           msg = conn.recv(1024).decode().strip()
           if not msg or msg == "/end":
               end_connection(conn, addr)
               break
           print(addr, ":", msg)
           server_respond(conn, "Message Recieved by the server\n")

def socket_run():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()
        threading.Thread(target=server_client_msg, args=(conn, )).start()

if __name__ == "__main__":
     socket_run()
