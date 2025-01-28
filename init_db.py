import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import logging
from typing import List, Dict

load_dotenv()

logging.basicConfig(level=logging.INFO)


def get_db_connection():
    """Create and return a PostgreSQL database connection"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL is not set. Check your environment variables.")
    return psycopg2.connect(dsn=database_url)


def init_db():
    """Initialize the PostgreSQL database and create tables"""
    try:
        with get_db_connection() as conn, conn.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    role VARCHAR(10) CHECK (role IN ('user', 'system')) NOT NULL,
                    content TEXT NOT NULL
                )
            ''')
            conn.commit()
            logging.info("Database initialized successfully")
    except Exception as e:
        logging.error(f"Error initializing database: {e}")


def store_message(role: str, content: str):
    """Store a message in the database"""
    try:
        with get_db_connection() as conn, conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO messages (role, content) VALUES (%s, %s)",
                (role, content)
            )
            conn.commit()
            logging.info("Message stored successfully")
    except Exception as e:
        logging.error(f"Error storing message: {e}")


def fetch_history(limit: int = 10) -> List[Dict]:
    """Fetch chat history from the database"""
    if limit <= 0:
        raise ValueError("Limit must be greater than 0")
    try:
        with get_db_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "SELECT * FROM messages ORDER BY timestamp DESC LIMIT %s",
                (limit,)
            )
            results = cursor.fetchall()
            logging.info(f"Fetched {len(results)} messages from history")
            return results
    except Exception as e:
        logging.error(f"Error fetching history: {e}")
        return []
