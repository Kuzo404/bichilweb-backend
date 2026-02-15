import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE','bichilglobusweb.settings')
import django; django.setup()
from app.models.models import Header
from app.serializers.headers import HeaderSerializer
import json

h = Header.objects.filter(id=1).first()
s = HeaderSerializer(h)
d = s.data
print(f"menus: {len(d['menus'])}")
print(f"styles: {len(d['styles'])}")
for m in d['menus']:
    print(f"  menu id={m['id']}, path={m['path']}, index={m['index']}, trans={m['translations']}")
    for sm in m.get('submenus', []):
        print(f"    submenu id={sm['id']}, path={sm['path']}, trans={sm['translations']}")
for st in d['styles']:
    print(f"  style: {json.dumps(st)}")
print("\nDone!")
