import sqlite3
import sys
import os

db_path = os.path.join(os.path.dirname(__file__), 'legal_research.db')
if not os.path.exists(db_path):
    print("Database file does not exist")
    sys.exit(1)

conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = c.fetchall()

if not tables:
    print("No tables found in database.")

for table in tables:
    print(f'Table: {table[0]}')
    c.execute(f'PRAGMA table_info({table[0]});')
    columns = c.fetchall()
    for col in columns:
        print(f'  {col}')
