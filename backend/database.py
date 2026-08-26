"""
Database Repository Layer for LANDGUARD AI.
Handles SQLite connection pooling, SQL execution, and scope-based queries.
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent.parent
import sys
sys.path.insert(0, str(BASE_DIR))

from utils.config import DATABASE_PATH
from utils.logger import get_logger

logger = get_logger("BackendDatabase")

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def execute_query(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
    except Exception as e:
        logger.error(f"Database query error: {e} | Query: {query}")
        raise e
    finally:
        conn.close()

def execute_query_one(query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
    results = execute_query(query, params)
    return results[0] if results else None

def execute_write(query: str, params: tuple = ()) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        conn.commit()
        return cursor.rowcount
    except Exception as e:
        conn.rollback()
        logger.error(f"Database write error: {e} | Query: {query}")
        raise e
    finally:
        conn.close()
