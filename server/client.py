from server.colors import random_color

class ClientSession:
    def __init__(self, conn, addr):
        self.color = random_color()
        self.conn = conn
        self.addr = addr
        self.name = "Anon"
    
    def set_name(self, name: str) -> None:
        self.name = name.strip()

    def close(self) -> None:
        try:
            self.conn.close()
        except Exception:
            pass
