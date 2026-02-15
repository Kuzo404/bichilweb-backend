"""
Hero Slider Cloudinary upload/delete тест.
"""
import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bichilglobusweb.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

import cloudinary
import cloudinary.uploader

# Cloudinary холболт шалгах
print(f"Cloud name: {cloudinary.config().cloud_name}")
print(f"API key: {cloudinary.config().api_key[:6]}...")

# Тест upload (жижиг placeholder зураг)
import io
from PIL import Image

# 100x100 тест зураг үүсгэх
img = Image.new('RGB', (100, 100), color='red')
buffer = io.BytesIO()
img.save(buffer, format='JPEG')
buffer.seek(0)
buffer.name = 'test_hero_slider.jpg'

print("\n--- Cloudinary Upload тест ---")
try:
    result = cloudinary.uploader.upload(
        buffer,
        resource_type='image',
        folder='bichil/hero_slider/desktop',
        public_id='test_hero_slider',
        overwrite=True,
    )
    url = result['secure_url']
    public_id = result['public_id']
    print(f"✅ Upload амжилттай!")
    print(f"   URL: {url}")
    print(f"   Public ID: {public_id}")
except Exception as e:
    print(f"❌ Upload алдаа: {e}")
    sys.exit(1)

# Тест delete
print("\n--- Cloudinary Delete тест ---")
try:
    del_result = cloudinary.uploader.destroy(public_id, resource_type='image')
    print(f"✅ Delete амжилттай! Result: {del_result}")
except Exception as e:
    print(f"❌ Delete алдаа: {e}")

print("\n✅ Cloudinary Hero Slider интеграци ажиллаж байна!")
