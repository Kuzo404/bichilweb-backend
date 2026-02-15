import psycopg2

conn = psycopg2.connect(
    host='dpg-d689vsur433s73ch0i8g-a.oregon-postgres.render.com',
    dbname='bichilweb_db_emzp',
    user='bichilweb_db_emzp_user',
    password='6TpyOr4jPpxZ3G75sBp8kpJrXvIrNa0v',
    port=5432
)
cur = conn.cursor()
cur.execute("ALTER TABLE app_download ADD COLUMN IF NOT EXISTS mobile_layout TEXT DEFAULT 'image-top'")
conn.commit()
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='app_download' AND column_name='mobile_layout'")
print('Column exists:', cur.fetchone())
conn.close()
print('Done!')
