import sqlite3

db_path = "synthetic_data.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print(f"Connected to {db_path}")

# Show all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("\nTables in database:")
for t in tables:
    print("-", t[0])

# Show first 5 rows of each table
for t in tables:
    print(f"\nPreview of table: {t[0]}")
    cursor.execute(f"SELECT * FROM {t[0]} LIMIT 1000;")
    for row in cursor.fetchall():
        print(row)

conn.close()
