"""CTA Cloudinary upload тест"""
import requests, io
from PIL import Image

img = Image.new('RGB', (400, 200), color='purple')
buf = io.BytesIO()
img.save(buf, format='JPEG')
buf.seek(0)

print("=== CTA Create (Cloudinary) ===")
r = requests.post('http://127.0.0.1:8000/api/v1/cta/',
    files={'file': ('test_cta.jpg', buf, 'image/jpeg')},
    data={
        'number': '01',
        'index': '99',
        'font': 'Arial',
        'color': '#ffffff',
        'description': 'test',
        'url': '/test',
    },
    timeout=30)
print(f'Status: {r.status_code}')
d = r.json()

if r.status_code == 201:
    print(f'file: {d.get("file", "N/A")}')
    print(f'file_url: {d.get("file_url", "N/A")}')
    is_cloud = 'cloudinary.com' in str(d.get('file', ''))
    print(f'Cloudinary: {"YES" if is_cloud else "NO"}')
    
    # Delete test
    cta_id = d['id']
    r2 = requests.delete(f'http://127.0.0.1:8000/api/v1/cta/{cta_id}/')
    print(f'Delete: {r2.status_code}')
    print('OK!')
else:
    print(f'Error: {d}')
