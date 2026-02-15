"""Video upload тест"""
import requests, io

buf = io.BytesIO(b'\x00\x00\x00\x1cftypisom' + b'\x00' * 500)
buf.seek(0)
r = requests.post('http://127.0.0.1:8000/api/v1/hero-slider/',
    files={'file': ('test_video.mp4', buf, 'video/mp4')},
    data={'type': 'v', 'time': '10', 'index': '99', 'visible': '1'},
    timeout=60)
print(f'Status: {r.status_code}')
try:
    d = r.json()
    if r.status_code == 201:
        print(f'OK: {d["file"][:80]}')
        sid = d['id']
        r2 = requests.delete(f'http://127.0.0.1:8000/api/v1/hero-slider/{sid}/')
        print(f'Delete: {r2.status_code}')
    else:
        print(f'Detail: {d.get("detail", d)}')
except:
    print(r.text[:300])
