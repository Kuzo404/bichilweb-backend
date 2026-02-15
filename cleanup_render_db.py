"""
Render DB дээрх давхардсан header өгөгдлийг цэвэрлэх.
Header 1-г үлдээж, бусдыг устгана.
Header 1-ийн цэснүүдийг бүгдийг устгана (admin-аас дахин хадгална).
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bichilglobusweb.settings')
import django
django.setup()
from django.db import connection

cursor = connection.cursor()

print("=== Render DB цэвэрлэх ===\n")

# 1. Одоогийн тоо ширхэг
cursor.execute("SELECT COUNT(*) FROM header")
print(f"Headers: {cursor.fetchone()[0]}")
cursor.execute("SELECT COUNT(*) FROM header_menu")
print(f"Total menus: {cursor.fetchone()[0]}")
cursor.execute("SELECT COUNT(*) FROM header_menu_translation")
print(f"Total menu translations: {cursor.fetchone()[0]}")
cursor.execute("SELECT COUNT(*) FROM header_submenu")
print(f"Total submenus: {cursor.fetchone()[0]}")
cursor.execute("SELECT COUNT(*) FROM header_submenu_translation")
print(f"Total submenu translations: {cursor.fetchone()[0]}")
cursor.execute("SELECT COUNT(*) FROM header_tertiary_menu")
print(f"Total tertiary menus: {cursor.fetchone()[0]}")
cursor.execute("SELECT COUNT(*) FROM header_style")
print(f"Total styles: {cursor.fetchone()[0]}")

# 2. Header 1-ийн хамгийн сүүлийн 5 цэсний index, path-г шалгах
cursor.execute("""
    SELECT id, path, "index", visible 
    FROM header_menu 
    WHERE header = 1 
    ORDER BY id DESC 
    LIMIT 5
""")
latest_menus = cursor.fetchall()
print(f"\nHeader 1 хамгийн сүүлийн 5 цэс:")
latest_menu_ids = []
for m in latest_menus:
    print(f"  id={m[0]}, path={m[1]}, index={m[2]}, visible={m[3]}")
    latest_menu_ids.append(m[0])

# Тэдний орчуулгуудыг шалгах
if latest_menu_ids:
    placeholders = ','.join(['%s'] * len(latest_menu_ids))
    cursor.execute(f"""
        SELECT t.menu, t.label, t.language 
        FROM header_menu_translation t 
        WHERE t.menu IN ({placeholders}) 
        ORDER BY t.menu, t.language
    """, latest_menu_ids)
    trans = cursor.fetchall()
    print(f"\nСүүлийн 5 цэсний орчуулга:")
    for t in trans:
        print(f"  menu={t[0]}, label={t[1]}, lang={t[2]}")

print(f"\n--- Хамгийн сүүлийн 5 цэсийг (id: {latest_menu_ids}) үлдээх үү? ---")
confirm = input("y/n: ").strip().lower()
if confirm != 'y':
    print("Цуцлав.")
    exit()

print("\n=== Цэвэрлэж байна... ===")

# 3. Header 1-ийн сүүлийн 5-аас бусад цэснүүдийн tertiary_menu, submenu, translation устгах
# CASCADE ажиллах ёстой, гэхдээ бат бөх байхын тулд гараар
if latest_menu_ids:
    placeholders = ','.join(['%s'] * len(latest_menu_ids))
    
    # Хуучин цэснүүдийн submenus-ийн tertiary menus
    cursor.execute(f"""
        DELETE FROM header_tertiary_menu_translation 
        WHERE tertiary_menu IN (
            SELECT tm.id FROM header_tertiary_menu tm
            JOIN header_submenu sm ON tm.header_submenu = sm.id
            JOIN header_menu m ON sm.header_menu = m.id
            WHERE m.header = 1 AND m.id NOT IN ({placeholders})
        )
    """, latest_menu_ids)
    print(f"  Deleted tertiary_menu_translations: {cursor.rowcount}")
    
    cursor.execute(f"""
        DELETE FROM header_tertiary_menu 
        WHERE header_submenu IN (
            SELECT sm.id FROM header_submenu sm
            JOIN header_menu m ON sm.header_menu = m.id
            WHERE m.header = 1 AND m.id NOT IN ({placeholders})
        )
    """, latest_menu_ids)
    print(f"  Deleted tertiary_menus: {cursor.rowcount}")
    
    cursor.execute(f"""
        DELETE FROM header_submenu_translation 
        WHERE submenu IN (
            SELECT sm.id FROM header_submenu sm
            JOIN header_menu m ON sm.header_menu = m.id
            WHERE m.header = 1 AND m.id NOT IN ({placeholders})
        )
    """, latest_menu_ids)
    print(f"  Deleted submenu_translations: {cursor.rowcount}")
    
    cursor.execute(f"""
        DELETE FROM header_submenu 
        WHERE header_menu IN (
            SELECT id FROM header_menu 
            WHERE header = 1 AND id NOT IN ({placeholders})
        )
    """, latest_menu_ids)
    print(f"  Deleted submenus: {cursor.rowcount}")
    
    cursor.execute(f"""
        DELETE FROM header_menu_translation 
        WHERE menu IN (
            SELECT id FROM header_menu 
            WHERE header = 1 AND id NOT IN ({placeholders})
        )
    """, latest_menu_ids)
    print(f"  Deleted menu_translations: {cursor.rowcount}")
    
    cursor.execute(f"""
        DELETE FROM header_menu 
        WHERE header = 1 AND id NOT IN ({placeholders})
    """, latest_menu_ids)
    print(f"  Deleted old menus: {cursor.rowcount}")

# 4. Бусад header-уудыг (id != 1) бүрэн устгах
# Тэдний цэснүүд, орчуулга, стиль бүгдийг
for table in ['header_tertiary_menu_translation', 'header_tertiary_menu', 
              'header_submenu_translation', 'header_submenu',
              'header_menu_translation', 'header_menu', 'header_style']:
    cursor.execute(f"""
        DELETE FROM {table} 
        WHERE EXISTS (
            SELECT 1 FROM header_menu m 
            WHERE m.header != 1 
            AND (
                {table}.id IS NOT NULL
            )
        ) AND FALSE
    """)

# Actually just target by header FK
cursor.execute("DELETE FROM header_style WHERE header != 1")
print(f"  Deleted other header styles: {cursor.rowcount}")

# Delete menus of other headers (and their children via CASCADE hopefully)
cursor.execute("""
    DELETE FROM header_tertiary_menu_translation WHERE tertiary_menu IN (
        SELECT tm.id FROM header_tertiary_menu tm
        JOIN header_submenu sm ON tm.header_submenu = sm.id
        JOIN header_menu m ON sm.header_menu = m.id
        WHERE m.header != 1
    )
""")
print(f"  Deleted other tertiary translations: {cursor.rowcount}")

cursor.execute("""
    DELETE FROM header_tertiary_menu WHERE header_submenu IN (
        SELECT sm.id FROM header_submenu sm
        JOIN header_menu m ON sm.header_menu = m.id
        WHERE m.header != 1
    )
""")
print(f"  Deleted other tertiary menus: {cursor.rowcount}")

cursor.execute("""
    DELETE FROM header_submenu_translation WHERE submenu IN (
        SELECT sm.id FROM header_submenu sm
        JOIN header_menu m ON sm.header_menu = m.id
        WHERE m.header != 1
    )
""")
print(f"  Deleted other submenu translations: {cursor.rowcount}")

cursor.execute("""
    DELETE FROM header_submenu WHERE header_menu IN (
        SELECT id FROM header_menu WHERE header != 1
    )
""")
print(f"  Deleted other submenus: {cursor.rowcount}")

cursor.execute("DELETE FROM header_menu_translation WHERE menu IN (SELECT id FROM header_menu WHERE header != 1)")
print(f"  Deleted other menu translations: {cursor.rowcount}")

cursor.execute("DELETE FROM header_menu WHERE header != 1")
print(f"  Deleted other menus: {cursor.rowcount}")

cursor.execute("DELETE FROM header WHERE id != 1")
print(f"  Deleted other headers: {cursor.rowcount}")

# 5. Шалгах
print("\n=== Цэвэрлэсний дараа ===")
cursor.execute("SELECT COUNT(*) FROM header")
print(f"Headers: {cursor.fetchone()[0]}")
cursor.execute("SELECT COUNT(*) FROM header_menu WHERE header = 1")
print(f"Header 1 menus: {cursor.fetchone()[0]}")
cursor.execute("SELECT COUNT(*) FROM header_style WHERE header = 1")
print(f"Header 1 styles: {cursor.fetchone()[0]}")

print("\n✅ Амжилттай цэвэрлэгдлээ!")
