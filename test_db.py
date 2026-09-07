import sqlite3
import json
conn = sqlite3.connect('backend/database/attendance.db')
conn.row_factory = sqlite3.Row
c = conn.execute("SELECT COUNT(DISTINCT session_id) as c, subject_name FROM attendance WHERE institution_id='DEMO2026' GROUP BY subject_name")
for r in c.fetchall():
    print(r['subject_name'], r['c'])
