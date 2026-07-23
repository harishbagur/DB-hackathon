import sqlite3

db = sqlite3.connect('backend/hausbank.db')
c = db.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in c.fetchall()]

print("--- Database Tables ---")
for t in tables:
    count = c.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
    print(f"Table: {t} (Rows: {count})")
    
    # Fetch first row if it has data
    if count > 0:
        row = c.execute(f"SELECT * FROM {t} LIMIT 1").fetchone()
        columns = [desc[0] for desc in c.description]
        print(f"  Sample: {dict(zip(columns, row))}")
    print()
