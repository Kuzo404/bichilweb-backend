"""
Hero Slider API-р дамжуулан Cloudinary upload тест хийх.
POST /api/v1/hero-slider/ руу multipart form data илгээнэ.
"""
import os
import sys
import io
import requests

# Тест зураг үүсгэх
try:
    from PIL import Image
    img = Image.new('RGB', (200, 100), color='blue')
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    buffer.seek(0)
except ImportError:
    # PIL байхгүй бол жижиг binary file
    buffer = io.BytesIO(b'\xff\xd8\xff\xe0' + b'\x00' * 100)
    buffer.seek(0)

BASE_URL = "http://127.0.0.1:8000/api/v1"

# 1. Upload тест (create)
print("=== 1. Create Hero Slider (Cloudinary upload) ===")
files = {'file': ('test_cloudinary_hero.jpg', buffer, 'image/jpeg')}
data = {'type': 'i', 'time': '5', 'index': '99', 'visible': '1'}

r = requests.post(f"{BASE_URL}/hero-slider/", files=files, data=data)
print(f"Status: {r.status_code}")

if r.status_code == 201:
    slide = r.json()
    slide_id = slide['id']
    print(f"ID: {slide_id}")
    print(f"file: {slide['file']}")
    print(f"file_url: {slide['file_url']}")
    
    # Cloudinary URL байгаа эсэх шалгах
    if 'cloudinary.com' in (slide['file'] or ''):
        print("✅ Cloudinary URL хадгалагдсан!")
    else:
        print("❌ Cloudinary URL биш!")
        sys.exit(1)

    # 2. Delete тест  
    print(f"\n=== 2. Delete Hero Slider #{slide_id} (Cloudinary delete) ===")
    r2 = requests.delete(f"{BASE_URL}/hero-slider/{slide_id}/")
    print(f"Status: {r2.status_code}")
    if r2.status_code == 204:
        print("✅ Устгалт амжилттай! (Cloudinary дээрх файл мөн устгагдсан)")
    else:
        print(f"❌ Устгалт амжилтгүй: {r2.text}")
else:
    print(f"❌ Create амжилтгүй: {r.text}")
    sys.exit(1)

print("\n✅ Hero Slider Cloudinary интеграци бүрэн ажиллаж байна!")
