"""Video upload test - small fake mp4"""
import requests, io

# Бодит бага хэмжээний mp4 файл үүсгэх (ffmpeg-тэй бол)
import subprocess, tempfile, os

tmpdir = tempfile.gettempdir()
video_path = os.path.join(tmpdir, 'test_video.mp4')

# ffmpeg байгаа эсэхийг шалгах
try:
    subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
    has_ffmpeg = True
except Exception:
    has_ffmpeg = False

if has_ffmpeg:
    print('Creating test video with ffmpeg...')
    subprocess.run([
        'ffmpeg', '-y', '-f', 'lavfi', '-i', 'color=c=blue:s=320x240:d=2',
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', video_path
    ], capture_output=True, check=True)
    
    with open(video_path, 'rb') as f:
        print(f'Video size: {os.path.getsize(video_path)} bytes')
        r = requests.post('http://127.0.0.1:8000/api/v1/hero-slider/',
            files={'file': ('test_video.mp4', f, 'video/mp4')},
            data={'type': 'v', 'time': '2', 'index': '98', 'visible': '0'},
            timeout=120)
    
    print(f'Status: {r.status_code}')
    if r.status_code == 201:
        d = r.json()
        print(f"file: {d.get('file', 'N/A')}")
        is_cloud = 'cloudinary.com' in str(d.get('file', ''))
        print(f"Cloudinary: {'YES' if is_cloud else 'NO'}")
        sid = d['id']
        r2 = requests.delete(f'http://127.0.0.1:8000/api/v1/hero-slider/{sid}/')
        print(f'Cleanup: {r2.status_code}')
        print('SUCCESS!')
    else:
        print(f'Error: {r.text[:500]}')
else:
    print('ffmpeg not found, using raw bytes...')
    # Smallest valid mp4 header
    buf = io.BytesIO(b'\x00\x00\x00\x1c\x66\x74\x79\x70\x69\x73\x6f\x6d' + b'\x00' * 1000)
    r = requests.post('http://127.0.0.1:8000/api/v1/hero-slider/',
        files={'file': ('test_video.mp4', buf, 'video/mp4')},
        data={'type': 'v', 'time': '2', 'index': '98', 'visible': '0'},
        timeout=120)
    print(f'Status: {r.status_code}')
    if r.status_code == 201:
        d = r.json()
        print(f"file: {d.get('file', 'N/A')}")
        sid = d['id']
        requests.delete(f'http://127.0.0.1:8000/api/v1/hero-slider/{sid}/')
        print('SUCCESS!')
    else:
        print(f'Response: {r.text[:500]}')
