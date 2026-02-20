#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler

def run(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler):
    server_address = ('0.0.0.0', 8000)
    httpd = server_class(server_address, handler_class)
    print("Server running on port 8000...")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
