import sqlite3
import sys

for name in ["Database/learning_n.db", "Database/learning.db"]:
    print("====", name, "====")
    try:
        conn = sqlite3.connect(name)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cur.fetchall()
        print("Tables:", tables)
        for t in tables:
            tname = t[0]
            cur.execute(f"PRAGMA table_info({tname})")
            print(f"  Schema for {tname}:", cur.fetchall())
            cur.execute(f"SELECT * FROM {tname} LIMIT 5")
            print(f"  Sample rows:", cur.fetchall())
        conn.close()
    except Exception as e:
        print("ERROR:", e)
