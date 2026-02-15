import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE','bichilglobusweb.settings')
import django; django.setup()
from django.db import connection
c = connection.cursor()
c.execute('SELECT COUNT(*) FROM header_menu WHERE header = 1')
print(f'Header 1 total menus: {c.fetchone()[0]}')
c.execute('SELECT COUNT(*) FROM header_menu WHERE header = 1 AND visible = 1')
print(f'Header 1 visible menus: {c.fetchone()[0]}')
c.execute('SELECT DISTINCT header FROM header_menu ORDER BY header')
print(f'Headers with menus: {[r[0] for r in c.fetchall()]}')
# Check what Django API would return
from app.models.models import Header
from app.serializers.headers import HeaderSerializer
h = Header.objects.filter(id=1).first()
if h:
    s = HeaderSerializer(h)
    d = s.data
    print(f'\nDjango API result:')
    print(f'  menus: {len(d.get("menus",[]))}')
    print(f'  styles: {len(d.get("styles",[]))}')
    print(f'  logo: {str(d.get("logo",""))[:60]}')
    for m in d.get('menus', [])[:3]:
        print(f'  menu: id={m["id"]}, path={m["path"]}, trans={m.get("translations",[])}')
else:
    print('Header 1 not found!')
