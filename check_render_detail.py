"""Render DB дээрх header өгөгдлийг дэлгэрэнгүй шалгах"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bichilglobusweb.settings')
import django
django.setup()
from django.db import connection

cursor = connection.cursor()

# Header бичлэгүүд
cursor.execute("SELECT id, logo, active FROM header ORDER BY id LIMIT 5")
rows = cursor.fetchall()
print("=== Headers (first 5) ===")
for r in rows:
    print(f"  id={r[0]}, logo={str(r[1])[:60]}, active={r[2]}")

# Header 1-ийн цэснүүд
cursor.execute("SELECT id, header, path, font, \"index\", visible FROM header_menu WHERE header = 1 ORDER BY \"index\" LIMIT 10")
menus = cursor.fetchall()
print(f"\n=== Header 1 menus ({len(menus)}) ===")
for m in menus:
    print(f"  id={m[0]}, path={m[2]}, index={m[4]}, visible={m[5]}")

# Header 1 menu translations
if menus:
    menu_ids = [m[0] for m in menus]
    placeholders = ','.join(['%s'] * len(menu_ids))
    cursor.execute(f"SELECT id, menu, label, language_id FROM header_menu_translation WHERE menu IN ({placeholders}) ORDER BY menu, language_id", menu_ids)
    trans = cursor.fetchall()
    print(f"\n=== Header 1 menu translations ({len(trans)}) ===")
    for t in trans:
        print(f"  menu={t[1]}, label={t[2]}, lang={t[3]}")

# Header style
cursor.execute('SELECT id, header, "bgColor", "fontColor", "hoverColor", height, sticky, max_width, logo_size FROM header_style WHERE header = 1')
styles = cursor.fetchall()
print(f"\n=== Header 1 styles ({len(styles)}) ===")
for s in styles:
    print(f"  id={s[0]}, bg={s[2]}, font={s[3]}, hover={s[4]}, h={s[5]}, sticky={s[6]}, max_w={s[7]}, logo_s={s[8]}")

# Total counts
cursor.execute("SELECT header, COUNT(*) FROM header_menu GROUP BY header ORDER BY header LIMIT 10")
print(f"\n=== Menu counts per header ===")
for r in cursor.fetchall():
    print(f"  header {r[0]}: {r[1]} menus")

print("\nDone!")
