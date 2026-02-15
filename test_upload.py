import requests, io
from PIL import Image

img = Image.new('RGB', (800, 400), color='red')
buf = io.BytesIO()
img.save(buf, format='JPEG')
buf.seek(0)

print('=== Hero Slider Image Upload Test ===')
r = requests.post('http://127.0.0.1:8000/api/v1/hero-slider/',
    files={'file': ('test_hero.jpg', buf, 'image/jpeg')},
    data={'type': 'i', 'time': '5', 'index': '99', 'visible': '1'},
    timeout=30)
print(f'Status: {r.status_code}')
if r.status_code == 201:
    d = r.json()
    print(f"file: {d.get('file', 'N/A')}")
    is_cloud = 'cloudinary.com' in str(d.get('file', ''))
    print(f"Cloudinary: {'YES' if is_cloud else 'NO'}")
    sid = d['id']
    r2 = requests.delete(f'http://127.0.0.1:8000/api/v1/hero-slider/{sid}/')
    print(f'Cleanup: {r2.status_code}')
else:
    print(f'Error: {r.text[:300]}')
