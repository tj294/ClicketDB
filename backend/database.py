import sqlite3
from dotenv import load_dotenv
from os import getenv
load_dotenv()
DB_NAME = getenv("DBNAME")


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn
