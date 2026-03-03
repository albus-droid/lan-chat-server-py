# Colors for terminal output
import random

RESET  = "\033[0m"
BOLD   = "\033[1m"

RED    = "\033[31m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
BLUE   = "\033[34m"
MAGENTA= "\033[35m"
CYAN   = "\033[36m"
GRAY   = "\033[90m"

def color(text: str, code: str) -> str:
    return f"{code}{text}{RESET}"

USER_COLORS = [GREEN, CYAN, RED, BLUE]

def random_color():
    return random.choice(USER_COLORS)