import psycopg
from datetime import datetime

conn = psycopg.connect('users.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL
    )
''')
conn.commit()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS daily_usage (
        user_id INTEGER REFERENCES users(id),
        date DATE NOT NULL,
        usage_count INTEGER DEFAULT 0,
        PRIMARY KEY (user_id, date)
    )
''')
conn.commit()
        
def is_allowed_message(id):
    with psycopg.connect("dbname=example") as conn:
        with conn.cursor() as cur:
            today = datetime.today().date()
            cur.execute("SELECT usage_count FROM daily_usage WHERE user_id = %s AND date = %s", (id, today))
            result = cur.fetchone()
            if result and result[0] >= 50:
                return False
            else:
                if result:
                    cur.execute("UPDATE daily_usage SET usage_count = usage_count + 1 WHERE user_id = %s AND date = %s", (id, today))
                else:
                    cur.execute("INSERT INTO daily_usage (user_id, date, usage_count) VALUES (%s, %s, 1)", (id, today))
                conn.commit()
                return True