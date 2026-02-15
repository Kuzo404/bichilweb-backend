"""
Add featured_heading_en and latest_heading_en to news_page_settings table.
"""
import psycopg2, sys

conn = psycopg2.connect(
    host="dpg-d689vsur433s73ch0i8g-a.oregon-postgres.render.com",
    port=5432,
    dbname="bichilweb_db_emzp",
    user="bichilweb_db_emzp_user",
    password="6TpyOr4jPpxZ3G75sBp8kpJrXvIrNa0v",
    sslmode="require",
)
conn.autocommit = True
cur = conn.cursor()

columns = [
    ("news_page_settings", "featured_heading_en", "TEXT DEFAULT ''"),
    ("news_page_settings", "latest_heading_en", "TEXT DEFAULT ''"),
]

for table, col, col_type in columns:
    try:
        cur.execute(f'ALTER TABLE "{table}" ADD COLUMN "{col}" {col_type};')
        print(f"OK  added {table}.{col}")
    except psycopg2.errors.DuplicateColumn:
        conn.rollback()
        conn.autocommit = True
        print(f"--  {table}.{col} already exists")

cur.close()
conn.close()
print("Done.")
