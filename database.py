import sqlite3

DB_PATH = "complaints.db"

def init_db():
    """Initialize the database and create table if not exists."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            department TEXT,
            complaint TEXT,
            priority TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_complaint(name, department, complaint, priority):
    """Save a new complaint into the database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO complaints (name, department, complaint, priority)
        VALUES (?, ?, ?, ?)
    """, (name, department, complaint, priority))
    conn.commit()
    conn.close()

def read_complaints():
    """Read all complaints from the database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM complaints")
    rows = c.fetchall()
    conn.close()
    return rows
