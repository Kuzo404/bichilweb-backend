"""Render DB дээрх header өгөгдлийг шалгах"""
import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE','bichilglobusweb.settings')
import django; django.setup()
from django.db import connection

c = connection.cursor()
c.execute("SELECT COUNT(*) FROM header")
print(f"Headers: {c.fetchone()[0]}")
c.execute("SELECT id, logo, active FROM header ORDER BY id")
for r in c.fetchall():
    print(f"  id={r[0]}, logo={str(r[1])[:50]}, active={r[2]}")

c.execute("SELECT header, COUNT(*) as cnt FROM header_menu GROUP BY header ORDER BY header")
print(f"\nMenus per header:")
for r in c.fetchall():
    print(f"  header {r[0]}: {r[1]} menus")

c.execute("SELECT COUNT(*) FROM header_menu")
print(f"\nTotal menus: {c.fetchone()[0]}")
c.execute("SELECT COUNT(*) FROM header_style")
print(f"Total styles: {c.fetchone()[0]}")
