# ui/display.py

import os
import sys

# COLORS
RESET = "\033[0m"
BOLD = "\033[1m"

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
CYAN = "\033[36m"
WHITE = "\033[37m"
GRAY = "\033[90m"

BRIGHT_BLUE = "\033[94m"
BRIGHT_GREEN = "\033[92m"
BRIGHT_CYAN = "\033[96m"

THEME_ADMIN = BRIGHT_GREEN
THEME_VOTER = BRIGHT_BLUE
THEME_LOGIN = BRIGHT_CYAN


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def header(title, color):
    width = 60
    print(color + "═" * width + RESET)
    print(color + BOLD + title.center(width) + RESET)
    print(color + "═" * width + RESET)


def subheader(text, color):
    print(f"\n{color}{BOLD}▸ {text}{RESET}")


def menu_item(number, text, color):
    print(f"{color}{number}. {text}{RESET}")


def success(msg):
    print(f"{GREEN}✔ {msg}{RESET}")


def error(msg):
    print(f"{RED}✖ {msg}{RESET}")


def warning(msg):
    print(f"{YELLOW}! {msg}{RESET}")


def info(msg):
    print(f"{GRAY}{msg}{RESET}")


def prompt(text):
    return input(f"{WHITE}{text}: {RESET}")
