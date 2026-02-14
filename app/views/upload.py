"""
Зураг, видео upload хийх API view.
Файлуудыг Django-ийн media хавтаст хадгалаад URL-ийг буцаана.
"""
import os
import uuid
import mimetypes
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status


class FileUploadView(APIView):
    """
    POST /api/v1/upload/
    Зураг, видео, баримт файлуудыг media/ хавтаст хадгална.
    Буцаах: { "url": "/media/uploads/filename.ext", "file_type": "image|video|document" }
    """
    parser_classes = (MultiPartParser, FormParser)
    
    # Дүлхүүрт өврүүлэх боломжтой файл төрлүүд
    ALLOWED_MIME_TYPES = {
        # Зураг
        'image/jpeg': 'image',
        'image/png': 'image',
        'image/gif': 'image',
        'image/webp': 'image',
        'image/svg+xml': 'image',
        # Видео
        'video/mp4': 'video',
        'video/webm': 'video',
        'video/quicktime': 'video',
        'video/mpeg': 'video',
        'video/x-msvideo': 'video',
        # Баримт
        'application/pdf': 'document',
        'application/msword': 'document',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'document',
    }

    def post(self, request, *args, **kwargs):
        try:
            file_obj = request.FILES.get('file')
            if not file_obj:
                return Response(
                    {'error': 'Файл олдсонгүй. "file" талбараар илгээнэ үү.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Файлын MIME type шалгах
            mime_type, _ = mimetypes.guess_type(file_obj.name)
            if not mime_type:
                mime_type = file_obj.content_type

            # Дүлхүүрт өвөрүүлэх боломжтой төрөлүүдэнгүүлэх эсэхийг шалгах
            if mime_type not in self.ALLOWED_MIME_TYPES:
                return Response(
                    {
                        'error': f'Уг төрлийн файл дүлхүүрт өвөрүүлэх боломжгүй байна. MIME type: {mime_type}',
                        'allowed_types': list(self.ALLOWED_MIME_TYPES.keys())
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Файлын хэмжээ шалгах (100MB)
            file_size = file_obj.size
            max_size = 100 * 1024 * 1024  # 100MB
            if file_size > max_size:
                return Response(
                    {
                        'error': f'Файлын хэмжээ хэт их байна. Хамгийн дээд: {max_size / (1024*1024)}MB, таны файл: {file_size / (1024*1024):.2f}MB'
                    },
                    status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
                )

            # Файлын төрлийг тодорхойлох
            file_type = self.ALLOWED_MIME_TYPES.get(mime_type, 'document')

            # Файлын нэрийг давхцахгүй болгох
            ext = os.path.splitext(file_obj.name)[1].lower()
            unique_name = f"{uuid.uuid4().hex}{ext}"

            # Хадгалах хавтас (төрлөөр хүлэх)
            upload_type_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', file_type)
            os.makedirs(upload_type_dir, exist_ok=True)

            # Файлыг хадгалах
            file_path = os.path.join(upload_type_dir, unique_name)
            with open(file_path, 'wb+') as dest:
                for chunk in file_obj.chunks(chunk_size=1024 * 1024):  # 1MB chunks
                    dest.write(chunk)

            # URL буцаах
            file_url = f"{settings.MEDIA_URL}uploads/{file_type}/{unique_name}"
            return Response(
                {
                    'url': file_url,
                    'file_url': file_url,
                    'filename': unique_name,
                    'file_type': file_type,
                    'mime_type': mime_type,
                    'size': file_size,
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': f'Файл хадгалахад алдаа гарлаа: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
