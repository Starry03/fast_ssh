from os import environ
from pathlib import Path
import sys

import keyring
from argparse import ArgumentParser
from loguru import logger
import pexpect
from pexpect.exceptions import EOF, TIMEOUT

from models.host import Host
from sql.sql_manager import SQLManager


class App:
    NAME: str = "fast_ssh"

    @staticmethod
    def __resource_path(relative_path: str) -> Path:
        base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
        return base_path / relative_path

    def __init__(self, parser: ArgumentParser) -> None:
        self.parser: ArgumentParser = parser
        self.db: SQLManager = SQLManager()
        self.user = environ["USER"]
        self.saved_password: str | None = self.__get_saved_password()
        self.__print_title()
        try:
            self.unlock()
        except ValueError as e:
            logger.error(e)
            exit(1)

    def __get_saved_password(self) -> str | None:
        return keyring.get_password(App.NAME, self.user)

    def __set_saved_password(self, password: str) -> None:
        keyring.set_password(App.NAME, self.user, password)

    def __delete_saved_password(self) -> None:
        keyring.delete_password(App.NAME, self.user)

    def __print_title(self) -> None:
        with open(self.__resource_path("data/ascii_art.txt"), "r") as f:
            print(f.read())

    def unlock(self):
        if self.saved_password is not None:
            self.db.unlocked = self.db.unlock(self.saved_password)
        if not self.db.unlocked:
            master_password = input("Enter the master password: ")
            if self.db.is_initialized():
                if not self.db.unlock(master_password):
                    raise ValueError("Unable to unlock the database with the configured master password.")
                keyring.set_password("fast_ssh", environ["USER"], master_password)
            else:
                self.db.initialize_master_password(master_password)

    def setup(self) -> None:
        if self.parser.reset:
            self.reset()
            exit(0)
        if self.parser.add:
            name, ip, username, password = self.parser.add_host
            self.db.add_host(name, ip, username, password)
            logger.info(f"Host '{name}' added successfully.")
        if self.parser.remove:
            name = self.parser.remove
            self.db.remove_host(name)
            logger.info(f"Host '{name}' removed successfully.")
        logger.info("Exit (0)")
        for host in self.db.get_hosts():
            logger.info(f"Host ({host['id']}): {host['name']} ({host['ip']}) - Username: {host['username']}")

    def reset(self) -> None:
        if self.db.reset_database():
            self.__delete_saved_password()
            logger.info("Master password reset. Please run the program again to set a new master password.")
        else:
            logger.error("No database found to reset.")

    def __request_connection_id(self) -> int:
        while True:
            connection_choice = input("Connection id: ")
            try:
                return int(connection_choice)
            except ValueError:
                logger.error("Connection id must be an integer.")

    def __insert_password_on_connection(self, host: Host, timeout: int = 5) -> bool:
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

    def __try_connection(self, _id) -> bool:
        host: Host = self.db.get_host(_id)
        if self.parser.timeout:
            res = self.__insert_password_on_connection(host, timeout=self.parser.timeout)
        else:
            res = self.__insert_password_on_connection(host)
        if not res:
            logger.error(f"Failed to connect to host '{host['name']}' ({host['ip']}).")
        return res

    def core(self) -> None:
        while True:
            _id = self.__request_connection_id()
            if _id == 0 or self.__try_connection(_id):
                break