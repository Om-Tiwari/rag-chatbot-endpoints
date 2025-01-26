import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
from typing import List, Dict

# Load environment variables
load_dotenv()

def get_db_connection():
    """Create and return a MySQL database connection"""
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )

def init_db():
    """Initialize the MySQL database and create tables"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                role ENUM('user', 'system'),
                content TEXT
            )
        ''')
        
        conn.commit()
        cursor.close()
        conn.close()
        
    except Error as e:
        print(f"Error initializing database: {e}")

def store_message(role: str, content: str):
    """Store a message in the database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO messages (role, content) VALUES (%s, %s)",
            (role, content)
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
    except Error as e:
        print(f"Error storing message: {e}")

def fetch_history(limit: int = 10) -> List[Dict]:
    """Fetch chat history from the database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(
            "SELECT * FROM messages ORDER BY timestamp DESC LIMIT %s",
            (limit,)
        )
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return results
        
    except Error as e:
        print(f"Error fetching history: {e}")
        return []