import os
from pathlib import Path
from urllib.parse import quote_plus
from flask import flash

#all functions and methods should be held here

def load_env_file(env_path: str = ".env") -> None:
    path = Path(env_path)
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if key:
            os.environ.setdefault(key, value)


load_env_file()



def env_flag(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


# DB_HOST = ("DB_HOST", "localhost")
# DB_PORT = ("DB_PORT", "3306")
# DB_USER = ("DB_USER", "root")
# DB_PASSWORD = ("DB_PASSWORD", "cset155")
# DB_NAME = ("DB_NAME", "luxemotordb")
# DB_ECHO = env_flag("DB_ECHO", True)
# DB_CREATE_DATABASE = env_flag("DB_CREATE_DATABASE", True)

DB_HOST = ("localhost")
DB_PORT = ("3306")
DB_USER = ("root")
DB_PASSWORD = ("cset155")
DB_NAME = ("luxemotordb")
DB_ECHO = env_flag("DB_ECHO", True)
DB_CREATE_DATABASE = env_flag("DB_CREATE_DATABASE", True)

# FLASK_SECRET_KEY = ("FLASK_SECRET_KEY", "change-me")

FLASK_SECRET_KEY = ("change-me")

_encoded_password = quote_plus(DB_PASSWORD)
_db_host_port = f"{DB_HOST}:{DB_PORT}" if DB_PORT else DB_HOST

MYSQL_SERVER_URL = f"mysql://{DB_USER}:{_encoded_password}@{_db_host_port}"
DATABASE_URL = f"{MYSQL_SERVER_URL}/{DB_NAME}"

# Utility function to flash messages from anywhere
def flash_message(message, category="info"):
    """
    Flash a message with a category (success, error, info, etc.)
    Usage (in other files):
        from main import flash_message
        flash_message("Your message", "success")
    """
    flash(message, category)
