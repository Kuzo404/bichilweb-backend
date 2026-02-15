import requests, io, json
from PIL import Image

img = Image.new('RGB', (400, 200), color='green')
buf = io.BytesIO()
img.save(buf, format='JPEG')
buf.seek(0)

print('Creating CTA...')
r = requests.post('http://127.0.0.1:8000/api/v1/CTA/',
    files={'file': ('test.jpg', buf, 'image/jpeg')},
    data={
        'number': '01',
        'index': '1',
        'font': 'Arial',
        'color': '#fff',
        'description': 'test',
        'url': '/test',
        'titles': json.dumps([{"language": 2, "label": "Test MN"}]),
        'subtitles': json.dumps([{"language": 2, "label": "Sub MN"}]),
    },
    timeout=30)

print(f'Create: {r.status_code}')
if r.status_code == 201:
    d = r.json()
    cid = d['id']
    print(f'Created id={cid}, file={d.get("file","")}')
    
    # Now try delete
    print('Deleting...')
    r2 = requests.delete(f'http://127.0.0.1:8000/api/v1/CTA/{cid}/')
    print(f'Delete status: {r2.status_code}')
    if r2.status_code >= 300:
        print(f'Delete body: {r2.text[:500]}')
    else:
        print('Delete OK!')
else:
    print(f'Error: {r.text[:500]}')
