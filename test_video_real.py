"""Video upload тест - бодит видео"""
import requests, io, subprocess, os, tempfile

# ffmpeg ашиглан 1 секундын тест видео үүсгэх
tmp = os.path.join(tempfile.gettempdir(), 'test_hero.mp4')
try:
    subprocess.run([
        'ffmpeg', '-y', '-f', 'lavfi', '-i', 'color=c=blue:s=320x240:d=1',
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', tmp
    ], capture_output=True, timeout=10)
    has_ffmpeg = os.path.exists(tmp) and os.path.getsize(tmp) > 0
except Exception:
    has_ffmpeg = False

if not has_ffmpeg:
    # ffmpeg байхгүй бол зураг дээр тест хийх
    from PIL import Image
    img = Image.new('RGB', (200, 100), color='red')
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    buf.seek(0)
    print("ffmpeg олдсонгүй, зураг дээр тестлэнэ...")
    r = requests.post('http://127.0.0.1:8000/api/v1/hero-slider/',
        files={'file': ('test_img.jpg', buf, 'image/jpeg')},
        data={'type': 'i', 'time': '5', 'index': '99', 'visible': '1'},
        timeout=60)
else:
    print(f"Тест видео: {os.path.getsize(tmp)} bytes")
    with open(tmp, 'rb') as f:
        r = requests.post('http://127.0.0.1:8000/api/v1/hero-slider/',
            files={'file': ('test_hero.mp4', f, 'video/mp4')},
            data={'type': 'v', 'time': '1', 'index': '99', 'visible': '1'},
            timeout=60)

print(f'Status: {r.status_code}')
d = r.json()
if r.status_code == 201:
    print(f'File URL: {d["file"][:80]}...')
    is_video = '/video/' in d['file']
    print(f'Cloudinary resource: {"video" if is_video else "image"}')
    # Устгах
    sid = d['id']
    r2 = requests.delete(f'http://127.0.0.1:8000/api/v1/hero-slider/{sid}/')
    print(f'Delete: {r2.status_code}')
    print('OK!')
else:
    print(f'Error: {d.get("detail", d)}')

# Cleanup
if os.path.exists(tmp):
    os.remove(tmp)
