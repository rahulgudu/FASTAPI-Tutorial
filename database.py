import sqlite3

DB_NAME="board_meetings_raw.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    
    conn.row_factory = sqlite3.Row  # This allows us to access columns by name
    
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create a sample table for board meetings
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS board_meetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            agenda TEXT NOT NULL,
            is_confidential BOOLEAN NOT NULL DEFAULT FALSE
        )
    ''')
    
    conn.commit()
    conn.close()