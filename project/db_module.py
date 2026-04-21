import os
from pathlib import Path
from db.sqlite_db import SQLiteDatabase
from db.mssql_db import MSSQLDatabase
import sqlite3

# Try to import pymssql, handle gracefully if missing
try:
    import pymssql
except ImportError:
    pymssql = None

DB_FILE = Path(__file__).parent / 'data' / 'cinebase.db'
AUTH_FILE = Path(__file__).parent / 'config' / 'auth.cfg'

def get_database():
    """
    Factory function to select and initialize the appropriate database implementation.
    Selection priority:
    1. auth.cfg 'db_type' setting (explicit)
    2. Local cinebase.db file (automatic SQLite)
    3. Fallback to Mock (BaseDatabase)
    """
    db_type = None
    config = {}

    # 1. Read Config
    if AUTH_FILE.exists():
        with open(AUTH_FILE, 'r') as f:
            for line in f:
                if '=' in line:
                    key, val = line.strip().split('=')
                    config[key] = val
        db_type = config.get('db_type')

    # 2. Logic to select and connect
    
    # CASE A: Explicit SQLite or Auto-detect SQLite
    if db_type == 'sqlite' or (db_type is None and DB_FILE.exists()):
        try:
            connection = sqlite3.connect(DB_FILE, check_same_thread=False)
            print("Database Interface: SQLite (Modular)")
            return SQLiteDatabase(connection)
        except Exception as e:
            print(f"Failed to connect to SQLite: {e}")

    # CASE B: Explicit MSSQL or Auto-detect MSSQL (if auth.cfg has credentials)
    if db_type == 'mssql' or (db_type is None and config.get('username') and config.get('password')):
        if not pymssql:
            print("Error: pymssql not installed. Cannot use MSSQL backend.")
        else:
            try:
                connection = pymssql.connect(
                    server='uranium.cs.umanitoba.ca',
                    user=config['username'],
                    password=config['password'],
                    database='cs3380',
                    timeout=5
                )
                print("Database Interface: MSSQL (Modular)")
                return MSSQLDatabase(connection)
            except Exception as e:
                print(f"Failed to connect to MSSQL: {e}")

    # CASE C: Mock Mode
    print("Database Interface: Mock Mode (No connection)")
    return SQLiteDatabase(None) # SQLiteDatabase(None) works as a mock

# Legacy class alias for backward compatibility if needed
class Database:
    def __new__(cls, connection=None):
        # This allows Database() to still work but return the correct implementation
        if connection:
            if isinstance(connection, sqlite3.Connection):
                return SQLiteDatabase(connection)
            return MSSQLDatabase(connection)
        return get_database()
