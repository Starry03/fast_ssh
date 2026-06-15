import argparse
import sys

from loguru import logger
import pexpect
from pexpect.exceptions import EOF, TIMEOUT

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
    parser.add_argument("--add-host", nargs=4, metavar=("NAME", "IP", "USERNAME", "PASSWORD"),
                        help="Add a new host to the database")
    parser.add_argument("--list-hosts", action="store_true", help="List all hosts in the database")
    parser.add_argument("--remove-host", metavar="ID", help="Remove a host from the database by name")
    parser.add_argument("--reset-master-password", action="store_true",
                        help="Reset the master password (will require re-entering all host information)")
    parser.add_argument("--version", action="version", version="%(prog)s 1.0")
    parser.add_argument("--time-out", metavar="SECONDS", type=int, help="Timeout (seconds)")

    args = parser.parse_args()

    with open("./assets/ascii_art.txt", "r") as f:
        print(f.read())

    if args.reset_master_password:
        if SQLManager.reset_database():
            logger.info("Master password reset. Please run the program again to set a new master password.")
        else:
            logger.error("No database found to reset.")
        return None

    db = SQLManager()
    master_password = input("Enter the master password: ")

    if db.is_initialized():
        if not db.unlock(master_password):
            raise ValueError("Unable to unlock the database with the configured master password.")
    else:
        db.initialize_master_password(master_password)

    logger.info("Database unlocked successfully.")

    if args.add_host:
        name, ip, username, password = args.add_host
        db.add_host(name, ip, username, password)
        logger.info(f"Host '{name}' added successfully.")

    if args.remove_host:
        name = args.remove_host
        db.remove_host(name)
        logger.info(f"Host '{name}' removed successfully.")

    for host in db.get_hosts():
        logger.info(f"Host ({host['id']}): {host['name']} ({host['ip']}) - Username: {host['username']}")

    while True:
        while True:
            connection_choice = input("Connection id: ")
            try:
                connection_choice_idx = int(connection_choice)
                break
            except ValueError:
                logger.error("Connection id must be an integer.")

        while True:
            try:
                host: Host = db.get_host(connection_choice_idx)
                if args.time_out:
                    res = insert_password_on_connection(host, timeout=args.time_out)
                else:
                    res = insert_password_on_connection(host)
                if not res:
                    logger.error("Failed to establish SSH connection.")
                return None
            except ValueError as e:
                logger.error(e)
                break


if __name__ == "__main__":
    main()
