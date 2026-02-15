"""
Render DB дээр 5 зөв цэсийг сэргээх скрипт.
Local DB-ээс уншаад Render DB-д бичнэ.
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bichilglobusweb.settings')
import django
django.setup()
from django.db import connection

cursor = connection.cursor()

# Одоогийн header 1-ийн цэсний тоо шалгах
cursor.execute("SELECT COUNT(*) FROM header_menu WHERE header = 1")
count = cursor.fetchone()[0]
print(f"Одоогийн Header 1 цэс: {count}")

if count > 0:
    print("Аль хэдийн цэс байна — сэргээх хэрэггүй.")
    exit()

print("\n=== 5 цэс нэмж байна... ===\n")

# 5 цэсний өгөгдөл (Монгол, Англи)
menus = [
    {"index": 0, "path": "/about", "visible": 1, "translations": [
        {"lang": 1, "label": "About us"}, {"lang": 2, "label": "Бидний тухай"}
    ], "submenus": [
        {"index": 0, "path": "/about/introduction", "visible": 1, "translations": [
            {"lang": 1, "label": "Introduction"}, {"lang": 2, "label": "Танилцуулга"}
        ]},
        {"index": 1, "path": "/about/management", "visible": 1, "translations": [
            {"lang": 1, "label": "Management"}, {"lang": 2, "label": "Удирдлага"}
        ]},
        {"index": 2, "path": "/about/structure", "visible": 1, "translations": [
            {"lang": 1, "label": "Structure"}, {"lang": 2, "label": "Бүтэц"}
        ]},
    ]},
    {"index": 1, "path": "#", "visible": 1, "translations": [
        {"lang": 1, "label": "Product"}, {"lang": 2, "label": "Бүтээгдэхүүн"}
    ], "submenus": [
        {"index": 0, "path": "/products/loan", "visible": 1, "translations": [
            {"lang": 1, "label": "Loan"}, {"lang": 2, "label": "Зээл"}
        ]},
        {"index": 1, "path": "/products/savings", "visible": 1, "translations": [
            {"lang": 1, "label": "Savings"}, {"lang": 2, "label": "Хадгаламж"}
        ]},
    ]},
    {"index": 2, "path": "#", "visible": 1, "translations": [
        {"lang": 1, "label": "Service"}, {"lang": 2, "label": "Үйлчилгээ"}
    ], "submenus": [
        {"index": 0, "path": "/services/transfer", "visible": 1, "translations": [
            {"lang": 1, "label": "Transfer"}, {"lang": 2, "label": "Шилжүүлэг"}
        ]},
        {"index": 1, "path": "/services/exchange", "visible": 1, "translations": [
            {"lang": 1, "label": "Exchange"}, {"lang": 2, "label": "Валют"}
        ]},
    ]},
    {"index": 3, "path": "/news", "visible": 1, "translations": [
        {"lang": 1, "label": "News"}, {"lang": 2, "label": "Мэдээ"}
    ], "submenus": []},
    {"index": 4, "path": "/branches", "visible": 1, "translations": [
        {"lang": 1, "label": "Branches"}, {"lang": 2, "label": "Салбар"}
    ], "submenus": []},
]

for menu in menus:
    cursor.execute(
        'INSERT INTO header_menu (header, path, font, "index", visible) VALUES (1, %s, 0, %s, %s) RETURNING id',
        [menu["path"], menu["index"], menu["visible"]]
    )
    menu_id = cursor.fetchone()[0]
    print(f"  Menu {menu_id}: index={menu['index']}, path={menu['path']}")

    for t in menu["translations"]:
        cursor.execute(
            'INSERT INTO header_menu_translation (menu, language, label) VALUES (%s, %s, %s)',
            [menu_id, t["lang"], t["label"]]
        )

    for sub in menu.get("submenus", []):
        cursor.execute(
            'INSERT INTO header_submenu (header_menu, path, font, "index", visible) VALUES (%s, %s, 0, %s, %s) RETURNING id',
            [menu_id, sub["path"], sub["index"], sub["visible"]]
        )
        sub_id = cursor.fetchone()[0]
        print(f"    Submenu {sub_id}: index={sub['index']}, path={sub['path']}")

        for t in sub["translations"]:
            cursor.execute(
                'INSERT INTO header_submenu_translation (submenu, language, label) VALUES (%s, %s, %s)',
                [sub_id, t["lang"], t["label"]]
            )

print("\n=== Шалгалт ===")
cursor.execute("SELECT COUNT(*) FROM header_menu WHERE header = 1")
print(f"Header 1 цэс: {cursor.fetchone()[0]}")
cursor.execute("SELECT COUNT(*) FROM header_menu_translation")
print(f"Цэсний орчуулга: {cursor.fetchone()[0]}")
cursor.execute("SELECT COUNT(*) FROM header_submenu")
print(f"Дэд цэс: {cursor.fetchone()[0]}")
cursor.execute("SELECT COUNT(*) FROM header_submenu_translation")
print(f"Дэд цэсний орчуулга: {cursor.fetchone()[0]}")
print("\n✅ Амжилттай!")
