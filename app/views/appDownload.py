"""
App Download CRUD view.
Зургийг Cloudinary дээр хадгалаад, устгахад Cloudinary-с устгана.
"""
import re
from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
import cloudinary
import cloudinary.uploader
from django.conf import settings

from app.models.models import AppDownload, AppDownloadTitle, AppDownloadList
from app.serializers.appDownload import AppDownloadReadSerializer, AppDownloadWriteSerializer

# Cloudinary config баталгаажуулах
cloudinary.config(
    cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
    api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
    api_secret=settings.CLOUDINARY_STORAGE['API_SECRET'],
)


class AppDownloadViewSet(viewsets.ModelViewSet):
    queryset = AppDownload.objects.prefetch_related('titles', 'lists').all()
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return AppDownloadReadSerializer
        return AppDownloadWriteSerializer

    # ─── Cloudinary helper: upload ────────────────────────────────
    def _upload_to_cloudinary(self, file_obj):
        """Зургийг Cloudinary дээр upload хийнэ. secure_url буцаана."""
        name_without_ext = file_obj.name.rsplit('.', 1)[0] if '.' in file_obj.name else file_obj.name
        folder = "bichil/app_download"

        if hasattr(file_obj, 'temporary_file_path'):
            upload_source = file_obj.temporary_file_path()
        else:
            upload_source = file_obj

        result = cloudinary.uploader.upload(
            upload_source,
            resource_type='image',
            folder=folder,
            public_id=name_without_ext,
            overwrite=True,
            quality='auto',
            fetch_format='auto',
        )
        return result['secure_url']

    # ─── Cloudinary helper: delete ────────────────────────────────
    def _delete_from_cloudinary(self, url):
        """Cloudinary URL-с public_id гаргаж аваад устгана."""
        if not url or 'cloudinary.com' not in str(url):
            return
        try:
            match = re.search(r'/upload/v\d+/(.+)$', url)
            if not match:
                return
            public_id_with_ext = match.group(1)
            public_id = public_id_with_ext.rsplit('.', 1)[0]
            cloudinary.uploader.destroy(public_id, resource_type='image')
        except Exception as e:
            print(f"[AppDownload] Cloudinary delete алдаа: {e}")

    # ─── CREATE ───────────────────────────────────────────────────
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        image_file = request.FILES.get('image_file')

        try:
            if image_file:
                cloudinary_url = self._upload_to_cloudinary(image_file)
                data['image'] = cloudinary_url
        except Exception as e:
            return Response(
                {'detail': f'Cloudinary upload алдаа: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        serializer = self.get_serializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        read_serializer = AppDownloadReadSerializer(serializer.instance)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    # ─── UPDATE ───────────────────────────────────────────────────
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()
        image_file = request.FILES.get('image_file')

        try:
            if image_file:
                self._delete_from_cloudinary(instance.image)
                cloudinary_url = self._upload_to_cloudinary(image_file)
                data['image'] = cloudinary_url
        except Exception as e:
            return Response(
                {'detail': f'Cloudinary upload алдаа: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        serializer = self.get_serializer(instance, data=data, partial=partial, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        read_serializer = AppDownloadReadSerializer(serializer.instance)
        return Response(read_serializer.data)

    # ─── DELETE ───────────────────────────────────────────────────
    def destroy(self, request, *args, **kwargs):
        """Устгахад Cloudinary дээрх зургийг мөн устгана."""
        instance = self.get_object()
        self._delete_from_cloudinary(instance.image)

        AppDownloadTitle.objects.filter(app_download=instance).delete()
        AppDownloadList.objects.filter(app_download=instance).delete()

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
