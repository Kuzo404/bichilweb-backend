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

# Add EN fields to branches
for col in ['location_en', 'area_en', 'city_en', 'district_en', 'open_en']:
    try:
        cur.execute(f"ALTER TABLE branches ADD COLUMN {col} TEXT DEFAULT '';")
        print(f"✅ branches.{col} added")
    except Exception as e:
        print(f"⚠️ branches.{col}: {e}")
        conn.rollback()
        conn.autocommit = True

# Add EN button label fields to branch_page_settings
for col in ['popup_btn_label_en', 'card_btn_label_en', 'map_btn_label_en']:
    try:
        cur.execute(f"ALTER TABLE branch_page_settings ADD COLUMN {col} TEXT DEFAULT '';")
        print(f"✅ branch_page_settings.{col} added")
    except Exception as e:
        print(f"⚠️ branch_page_settings.{col}: {e}")
        conn.rollback()
        conn.autocommit = True

cur.close()
conn.close()
print("Migration complete!")
