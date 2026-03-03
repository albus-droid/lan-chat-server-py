# main.py
import signal
import logging

from server.server import Server

def main():
    server = Server(host="0.0.0.0", port=8080)
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")
    # shutdown signal handlers
    signal.signal(signal.SIGINT, lambda s, f: server.shutdown())
    signal.signal(signal.SIGTERM, lambda s, f: server.shutdown())

    server.start()

if __name__ == "__main__":
    main()