import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bichilglobusweb.settings')
django.setup()
from django.db import connection
cursor = connection.cursor()
cursor.execute("ALTER TABLE about_page_section ADD COLUMN IF NOT EXISTS image TEXT DEFAULT ''")
cursor.execute("ALTER TABLE about_page_section ADD COLUMN IF NOT EXISTS image_position TEXT DEFAULT 'right'")
print('Migration successful!')
