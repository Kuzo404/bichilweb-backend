"""
Файл хадгалах / устгах нэгдсэн модуль.
Cloudinary идэвхтэй бол Cloudinary руу, идэвхгүй бол local MEDIA_ROOT руу хадгална.

settings.py дээр USE_CLOUDINARY = True/False тохируулна.
"""
import os
import re
import uuid
import logging
import mimetypes
from django.conf import settings

logger = logging.getLogger(__name__)


def _is_cloudinary_enabled():
    return getattr(settings, 'USE_CLOUDINARY', False)


# ─── UPLOAD ────────────────────────────────────────────────────────
def upload_file(file_obj, folder='uploads', resource_type='image', **kwargs):
    """
    Файл upload хийх.
    Cloudinary идэвхтэй бол Cloudinary руу, идэвхгүй бол local media руу хадгална.
    Returns: URL string
    """
    if _is_cloudinary_enabled():
        import cloudinary.uploader
        # temporary_file_path байвал disk path ашиглах
        if hasattr(file_obj, 'temporary_file_path'):
            source = file_obj.temporary_file_path()
        else:
            source = file_obj

        name_without_ext = file_obj.name.rsplit('.', 1)[0] if '.' in file_obj.name else file_obj.name
        upload_kwargs = {
            'resource_type': resource_type,
            'folder': folder,
            'public_id': name_without_ext,
            'overwrite': True,
        }
        if resource_type == 'image':
            upload_kwargs['quality'] = 'auto'
            upload_kwargs['fetch_format'] = 'auto'
        upload_kwargs.update(kwargs)

        result = cloudinary.uploader.upload(source, **upload_kwargs)
        return result['secure_url']
    else:
        # ─── LOCAL FILE STORAGE ──────────────────────────────────
        ext = ''
        if hasattr(file_obj, 'name') and '.' in file_obj.name:
            ext = '.' + file_obj.name.rsplit('.', 1)[1]
        filename = f"{uuid.uuid4().hex}{ext}"
        save_dir = os.path.join(settings.MEDIA_ROOT, folder)
        os.makedirs(save_dir, exist_ok=True)
        filepath = os.path.join(save_dir, filename)
        with open(filepath, 'wb+') as f:
            for chunk in file_obj.chunks():
                f.write(chunk)
        return f"{settings.MEDIA_URL}{folder}/{filename}"


def upload_large_file(file_obj, folder='uploads', resource_type='video', **kwargs):
    """
    Том файл (видео) upload хийх.
    Cloudinary идэвхтэй бол upload_large() ашиглана.
    Local бол ердийн хадгалалт.
    """
    if _is_cloudinary_enabled():
        import cloudinary.uploader
        if hasattr(file_obj, 'temporary_file_path'):
            source = file_obj.temporary_file_path()
        else:
            source = file_obj

        name_without_ext = file_obj.name.rsplit('.', 1)[0] if '.' in file_obj.name else file_obj.name
        upload_kwargs = {
            'resource_type': resource_type,
            'folder': folder,
            'public_id': name_without_ext,
            'overwrite': True,
            'chunk_size': 6_000_000,
            'timeout': 600,
        }
        upload_kwargs.update(kwargs)

        result = cloudinary.uploader.upload_large(source, **upload_kwargs)
        return result['secure_url']
    else:
        return upload_file(file_obj, folder=folder, resource_type=resource_type, **kwargs)


# ─── DELETE ────────────────────────────────────────────────────────
def delete_file(url_or_path, resource_type='image'):
    """
    Файл устгах.
    Cloudinary URL бол Cloudinary-с устгана.
    Local path бол disk-с устгана.
    """
    if not url_or_path:
        return

    url_str = str(url_or_path)

    if 'cloudinary.com' in url_str:
        if not _is_cloudinary_enabled():
            return  # Cloudinary идэвхгүй бол алгасах
        try:
            import cloudinary.uploader
            # Resource type auto-detect from URL
            if '/video/upload/' in url_str:
                resource_type = 'video'
            match = re.search(r'/upload/v\d+/(.+)$', url_str)
            if match:
                public_id_with_ext = match.group(1)
                public_id = public_id_with_ext.rsplit('.', 1)[0]
                cloudinary.uploader.destroy(public_id, resource_type=resource_type)
        except Exception as e:
            logger.warning('[storage] Cloudinary delete error: %s', e)
    else:
        # Local file delete
        if url_str.startswith(settings.MEDIA_URL):
            rel_path = url_str[len(settings.MEDIA_URL):]
            local_path = os.path.join(settings.MEDIA_ROOT, rel_path)
            if os.path.exists(local_path):
                try:
                    os.remove(local_path)
                except Exception as e:
                    logger.warning('[storage] Local delete error: %s', e)
        elif url_str.startswith('media/') or url_str.startswith('/media/'):
            clean = url_str.lstrip('/').replace('media/', '', 1)
            local_path = os.path.join(settings.MEDIA_ROOT, clean)
            if os.path.exists(local_path):
                try:
                    os.remove(local_path)
                except Exception as e:
                    logger.warning('[storage] Local delete error: %s', e)
