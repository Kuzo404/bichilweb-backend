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

# Add logo_size column
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='footer' AND column_name='logo_size'")
if cur.fetchone():
    print("Column logo_size already exists")
else:
    cur.execute("ALTER TABLE footer ADD COLUMN logo_size TEXT DEFAULT '56'")
    conn.commit()
    print("Added logo_size column (default '56' = h-14 = 56px)")

conn.close()
print("Done!")
