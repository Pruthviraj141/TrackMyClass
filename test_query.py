import sqlite3
import json

conn = sqlite3.connect('backend/database/trackmyclass.db')  # or wherever the DB is
conn.row_factory = sqlite3.Row

cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Tables:", [r[0] for r in cursor.fetchall()])

