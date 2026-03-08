# main.py
import signal
import logging
import asyncio

from server.server import Server

def main():
    server = Server(host="0.0.0.0", port=8080)
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    loop.add_signal_handler(signal.SIGINT, server.shutdown)
    loop.add_signal_handler(signal.SIGTERM, server.shutdown)

    try:
        loop.run_until_complete(server.start())
    except RuntimeError:
        pass
    finally:
        pending = asyncio.all_tasks(loop)
        if pending:
            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        loop.close()

if __name__ == "__main__":
    main()