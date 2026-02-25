# Parse command-line arguments for the LAN chat server
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="LAN chat server")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--no-color", action="store_true")
    return parser.parse_args()