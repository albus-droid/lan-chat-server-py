import colors

class ClientSession:
    def __init__(self, conn, addr):
        self.color = colors.random_color()
        self.conn = conn
        self.addr = addr
        self.name = "Anon"
    
    def set_name(self, name: str) -> None:
        self.name = name.strip