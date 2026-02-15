"""Quick test of hero slider API"""
import requests, io, re
from PIL import Image

img = Image.new('RGB', (200, 100), color='blue')
buf = io.BytesIO()
img.save(buf, format='JPEG')
buf.seek(0)

r = requests.post(
    'http://127.0.0.1:8000/api/v1/hero-slider/',
    files={'file': ('test.jpg', buf, 'image/jpeg')},
    data={'type': 'i', 'time': '5', 'index': '99', 'visible': '1'}
)
print(f'Status: {r.status_code}')

if r.status_code == 201:
    data = r.json()
    print(f"file: {data['file']}")
    print(f"file_url: {data['file_url']}")
    if 'cloudinary.com' in str(data.get('file', '')):
        print("OK: Cloudinary URL!")
    
    # Now delete it
    sid = data['id']
    r2 = requests.delete(f'http://127.0.0.1:8000/api/v1/hero-slider/{sid}/')
    print(f"Delete status: {r2.status_code}")
else:
    try:
        print(r.json())
    except Exception:
        # Extract from HTML error page
        m = re.search(r'Exception Value:</th>\s*<td><pre>(.*?)</pre>', r.text, re.DOTALL)
        if m:
            print(f"Error: {m.group(1)}")
        else:
            m2 = re.search(r'exception_value">(.*?)</pre>', r.text, re.DOTALL)
            if m2:
                print(f"Error: {m2.group(1)}")
            else:
                print(r.text[:500])
