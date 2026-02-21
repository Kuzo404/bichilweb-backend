"""
Зураг, видео upload хийх API view.
Файлуудыг Cloudinary эсвэл local storage дээр хадгалаад URL-ийг буцаана.
"""
import mimetypes
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from app.utils.storage import upload_file, upload_large_file
class FileUploadView(APIView):
    """
    POST /api/v1/upload/
    Зураг, видео, баримт файлуудыг хадгална (Cloudinary эсвэл local storage).
    Буцаах: { "url": "file_url", "file_type": "image|video|document" }
    """
    parser_classes = (MultiPartParser, FormParser)
    
    # Дүлхүүрт өврүүлэх боломжтой файл төрлүүд
    ALLOWED_MIME_TYPES = {
        # Зураг
        'image/jpeg': {'type': 'image', 'resource_type': 'image'},
        'image/png': {'type': 'image', 'resource_type': 'image'},
        'image/gif': {'type': 'image', 'resource_type': 'image'},
        'image/webp': {'type': 'image', 'resource_type': 'image'},
        'image/svg+xml': {'type': 'image', 'resource_type': 'image'},
        # Видео
        'video/mp4': {'type': 'video', 'resource_type': 'video'},
        'video/webm': {'type': 'video', 'resource_type': 'video'},
        'video/quicktime': {'type': 'video', 'resource_type': 'video'},
        'video/mpeg': {'type': 'video', 'resource_type': 'video'},
        'video/x-msvideo': {'type': 'video', 'resource_type': 'video'},
        # Баримт
        'application/pdf': {'type': 'document', 'resource_type': 'raw'},
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
            file_config = self.ALLOWED_MIME_TYPES[mime_type]
            file_type = file_config['type']
            resource_type = file_config['resource_type']

            # Upload хийх (Cloudinary эсвэл local storage)
            try:
                folder = f"bichil/{file_type}"
                if resource_type == 'video':
                    file_url = upload_large_file(file_obj, folder=folder, resource_type=resource_type)
                else:
                    file_url = upload_file(file_obj, folder=folder, resource_type=resource_type)

                return Response(
                    {
                        'url': file_url,
                        'file_url': file_url,
                        'filename': file_obj.name,
                        'file_type': file_type,
                        'mime_type': mime_type,
                        'size': file_size,
                    },
                    status=status.HTTP_201_CREATED
                )
            except Exception as upload_error:
                return Response(
                    {'error': f'Upload алдаа: {str(upload_error)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Exception as e:
            return Response(
                {'error': f'Файл хадгалахад алдаа гарлаа: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

