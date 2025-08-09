import sqlite3

dbfile = 'calendar_events.db'  # Your DB file

# Connect to the database
conn = sqlite3.connect(dbfile)
cursor = conn.cursor()

# 1. List all tables in the database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables:", tables)

# 2. For each table, print its contents
for table_name in tables:
    print(f"\nContents of table {table_name[0]}:")
    cursor.execute(f"SELECT * FROM {table_name[0]}")
    rows = cursor.fetchall()
    for row in rows:
        print(row)

conn.close()
