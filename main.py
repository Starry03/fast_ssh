import argparse
from os import environ

from loguru import logger
import pexpect
from pexpect.exceptions import EOF, TIMEOUT

from app import App
from sql.sql_manager import SQLManager
from models.host import Host


def insert_password_on_connection(host: Host, timeout: int = 5) -> bool:
    child = pexpect.spawn(
        "ssh",
        [f"{host['username']}@{host['ip']}"],
        encoding="utf-8",
        timeout=timeout,
    )

    try:
        while True:
            index = child.expect(
                [
                    r"Are you sure you want to continue connecting \(yes/no/\[fingerprint\]\)\?",
                    r"[Pp]assword:",
                    EOF,
                    TIMEOUT,
                ]
            )

            if index == 0:
                child.sendline("yes")
            elif index == 1:
                child.sendline(host["password"])
                break
            elif index == 2:
                logger.error(f"SSH ended unexpectedly: {child.before.strip()}")
                return False
            else:
                logger.error("Timeout while waiting for the SSH password prompt.")
                return False

        child.interact()
    finally:
        if child.isalive():
            child.close()
    return True


def main():
    parser = argparse.ArgumentParser(description="Choose the ssh, with auto-login")
    parser.add_argument("--add", nargs=4, metavar=("NAME", "IP", "USERNAME", "PASSWORD"),
                        help="Add a new host to the database")
    parser.add_argument("--list", action="store_true", help="List all hosts in the database")
    parser.add_argument("--remove", metavar="ID", help="Remove a host from the database by name")
    parser.add_argument("--reset", action="store_true",
                        help="Reset the master password (will require re-entering all host information)")
    parser.add_argument("--version", action="version", version="%(prog)s 1.1")
    parser.add_argument("--timeout", metavar="SECONDS", type=int, help="Timeout (seconds)")

    args = parser.parse_args()
    app = App(args)
    app.setup()
    if not parser.list:
        app.core()

if __name__ == "__main__":
    main()
