"""
Add name_en column to branches and branch_category tables.
"""
import psycopg2

conn = psycopg2.connect(
    host="dpg-d689vsur433s73ch0i8g-a.oregon-postgres.render.com",
    dbname="bichilweb_db_emzp",
    user="bichilweb_db_emzp_user",
    password="6TpyOr4jPpxZ3G75sBp8kpJrXvIrNa0v",
    port=5432,
    sslmode="require",
)
conn.autocommit = True
cur = conn.cursor()

# Add name_en to branches
try:
    cur.execute("ALTER TABLE branches ADD COLUMN name_en TEXT DEFAULT '';")
    print("✅ branches.name_en added")
except Exception as e:
    if 'already exists' in str(e):
        print("⚠️ branches.name_en already exists")
    else:
        print(f"❌ branches.name_en error: {e}")

# Add name_en to branch_category
try:
    cur.execute("ALTER TABLE branch_category ADD COLUMN name_en TEXT DEFAULT '';")
    print("✅ branch_category.name_en added")
except Exception as e:
    if 'already exists' in str(e):
        print("⚠️ branch_category.name_en already exists")
    else:
        print(f"❌ branch_category.name_en error: {e}")

cur.close()
conn.close()
print("Migration complete!")
