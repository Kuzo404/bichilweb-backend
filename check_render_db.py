"""Render PostgreSQL-ийн хүснэгтүүдийг шалгах скрипт"""
import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bichilglobusweb.settings')

import django
django.setup()

from django.db import connection

cursor = connection.cursor()

# Бүх хүснэгтүүдийг жагсаах
cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename")
tables = [row[0] for row in cursor.fetchall()]
print(f"\n=== Render DB Tables ({len(tables)}) ===")
for t in tables:
    print(f"  {t}")

# Header хүснэгтүүд байгаа эсэхийг шалгах
header_tables = ['header', 'header_menu', 'header_menu_translation', 'header_submenu',
                 'header_submenu_translation', 'header_tertiary_menu', 
                 'header_tertiary_menu_translation', 'header_style']
print(f"\n=== Header Tables Check ===")
for ht in header_tables:
    exists = ht in tables
    status = "✅" if exists else "❌ БАЙХГҮЙ"
    print(f"  {ht}: {status}")

# Header өгөгдөл байгаа эсэх
if 'header' in tables:
    cursor.execute("SELECT COUNT(*) FROM header")
    count = cursor.fetchone()[0]
    print(f"\n  header rows: {count}")
    
if 'header_menu' in tables:
    cursor.execute("SELECT COUNT(*) FROM header_menu")
    count = cursor.fetchone()[0]
    print(f"  header_menu rows: {count}")

if 'header_style' in tables:
    cursor.execute("SELECT COUNT(*) FROM header_style")
    count = cursor.fetchone()[0]
    print(f"  header_style rows: {count}")
    # Баганууд шалгах
    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='header_style' ORDER BY ordinal_position")
    cols = [row[0] for row in cursor.fetchall()]
    print(f"  header_style columns: {cols}")

print("\n=== Done ===")
