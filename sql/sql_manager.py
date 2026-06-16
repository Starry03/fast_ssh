import base64
import os
import sqlite3
from pathlib import Path
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from models.host import Host


class SQLManager:
    def __init__(self, db_path: str | None = None):
        self.unlocked = False
        self.db_path = db_path or self.default_db_path()
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.setup()
        self.fernet = None

    @staticmethod
    def default_data_dir() -> Path:
        base_dir = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
        return base_dir / "fast_ssh"

    @classmethod
    def default_db_path(cls) -> str:
        data_dir = cls.default_data_dir()
        data_dir.mkdir(parents=True, exist_ok=True)
        return str(data_dir / "hosts.db")

    def setup(self):
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS hosts
                            (
                                id
                                INTEGER
                                PRIMARY
                                KEY
                                AUTOINCREMENT,
                                name
                                TEXT
                                NOT
                                NULL,
                                ip
                                TEXT
                                NOT
                                NULL,
                                username
                                TEXT
                                NOT
                                NULL,
                                password
                                TEXT
                                NOT
                                NULL
                            )
                            """)
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS security_config
                            (
                                key
                                TEXT
                                PRIMARY
                                KEY,
                                value
                                BLOB
                                NOT
                                NULL
                            )
                            """)
        self.conn.commit()

    def is_initialized(self) -> bool:
        self.cursor.execute("SELECT value FROM security_config WHERE key = 'salt'")
        return self.cursor.fetchone() is not None

    def _derive_key(self, master_password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480_000,
        )
        return base64.urlsafe_b64encode(kdf.derive(master_password.encode()))

    def initialize_master_password(self, master_password: str):
        if self.is_initialized():
            raise ValueError("Master password configured already.")

        salt = os.urandom(16)
        key = self._derive_key(master_password, salt)
        self.fernet = Fernet(key)

        verifier = self.fernet.encrypt(b"verified_token")
        self.cursor.execute(
            "INSERT INTO security_config (key, value) VALUES ('salt', ?)", (salt,)
        )
        self.cursor.execute(
            "INSERT INTO security_config (key, value) VALUES ('verifier', ?)", (verifier,)
        )
        self.conn.commit()

    def unlock(self, master_password: str) -> bool:
        if not self.is_initialized():
            raise ValueError("Database not initialized. Please set a master password first.")

        self.cursor.execute("SELECT value FROM security_config WHERE key = 'salt'")
        salt = self.cursor.fetchone()[0]

        key = self._derive_key(master_password, salt)
        fernet = Fernet(key)

        self.cursor.execute("SELECT value FROM security_config WHERE key = 'verifier'")
        verifier = self.cursor.fetchone()[0]

        try:
            decrypted = fernet.decrypt(verifier)
            if decrypted == b"verified_token":
                self.fernet = fernet
                return True
        except InvalidToken:
            pass

        return False

    def add_host(self, name: str, ip: str, username: str, plaintext_password: str):
        if self.fernet is None:
            raise PermissionError("Unlocked database required to add hosts. Please unlock the database first.")

        encrypted_password = self.fernet.encrypt(plaintext_password.encode()).decode()

        self.cursor.execute(
            "INSERT INTO hosts (name, ip, username, password) VALUES (?, ?, ?, ?)",
            (name, ip, username, encrypted_password)
        )
        self.conn.commit()

    def __decrypted_host(self, host: Host) -> Host:
        host_id, name, ip, username, encrypted_password = host

        try:
            decrypted_password = self.fernet.decrypt(encrypted_password.encode()).decode()
        except InvalidToken:
            decrypted_password = "Decryption failed"
        return {
            "id": host_id,
            "name": name,
            "ip": ip,
            "username": username,
            "password": decrypted_password
        }

    def get_host(self, _id: int) -> Host:
        if self.fernet is None:
            raise PermissionError("Unlocked database required to retrieve hosts. Please unlock the database first.")
        self.cursor.execute("SELECT * FROM hosts WHERE id = ?", (_id,))
        row = self.cursor.fetchone()
        if row is None:
            raise ValueError("Host not found.")
        return self.__decrypted_host(row)

    def get_hosts(self) -> list[Host]:
        if self.fernet is None:
            raise PermissionError("Unlocked database required to retrieve hosts. Please unlock the database first.")

        self.cursor.execute("SELECT id, name, ip, username, password FROM hosts")
        rows = self.cursor.fetchall()

        hosts = []
        for row in rows:
            hosts.append(self.__decrypted_host(row))

        return hosts

    def close(self):
        self.conn.close()

    @staticmethod
    def reset_database(db_path: str | None = None) -> bool:
        db_path = db_path or SQLManager.default_db_path()
        if not os.path.exists(db_path):
            return False

        conn = sqlite3.connect(db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS hosts")
            cursor.execute("DROP TABLE IF EXISTS security_config")
            conn.commit()
        finally:
            conn.close()

        return True

    def remove_host(self, _id):
        if self.fernet is None:
            raise PermissionError("Unlocked database required to remove hosts. Please unlock the database first.")

        self.cursor.execute("DELETE FROM hosts WHERE id = ?", (_id,))
        self.conn.commit()
