"""
Зураг upload хийх API view.
Зургийг Django-ийн media хавтаст хадгалаад URL-ийг буцаана.
"""
import os
import uuid
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status


class FileUploadView(APIView):
    """
    POST /api/v1/upload/
    Зураг файл хүлээн авч media/uploads/ хавтаст хадгална.
    Буцаах: { "url": "/media/uploads/filename.ext" }
    """
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response(
                {'error': 'Файл олдсонгүй. "file" талбараар илгээнэ үү.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Файлын нэрийг давхцахгүй болгох
        ext = os.path.splitext(file_obj.name)[1].lower()
        unique_name = f"{uuid.uuid4().hex}{ext}"

        # Хадгалах хавтас
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)

        # Файлыг хадгалах
        file_path = os.path.join(upload_dir, unique_name)
        with open(file_path, 'wb+') as dest:
            for chunk in file_obj.chunks():
                dest.write(chunk)

        # URL буцаах
        file_url = f"{settings.MEDIA_URL}uploads/{unique_name}"
        return Response(
            {'url': file_url, 'file_url': file_url, 'filename': unique_name},
            status=status.HTTP_201_CREATED
        )
