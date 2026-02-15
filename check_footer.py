import psycopg2, os
from dotenv import load_dotenv
load_dotenv()

conn = psycopg2.connect(
    dbname=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
)
cur = conn.cursor()
cur.execute("SELECT id, logo, svg, logotext FROM footer LIMIT 5")
rows = cur.fetchall()
for r in rows:
    print(f"id={r[0]}, logo='{r[1]}', svg_len={len(r[2]) if r[2] else 0}, logotext='{r[3]}'")

# Check columns
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='footer' ORDER BY ordinal_position")
cols = [c[0] for c in cur.fetchall()]
print(f"\nColumns: {cols}")

conn.close()
