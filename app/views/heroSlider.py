"""
Hero Slider CRUD view.
Зураг/видеог Cloudinary дээр хадгалаад, устгахад Cloudinary-с устгана.
"""
import re
import mimetypes
from rest_framework.viewsets import ModelViewSet
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
import cloudinary
import cloudinary.uploader

from app.models.models import HeroSlider
from app.serializers.heroSlider import HeroSliderSerializer


class HeroSliderViewSet(ModelViewSet):
    queryset = HeroSlider.objects.all()
    serializer_class = HeroSliderSerializer
    parser_classes = [MultiPartParser, FormParser]

    # ─── Cloudinary helper: upload ────────────────────────────────
    def _upload_to_cloudinary(self, file_obj, device='desktop'):
        """
        Файлыг Cloudinary дээр upload хийнэ.
        device: 'desktop' | 'tablet' | 'mobile' — folder ялгах
        Буцаах: Cloudinary secure_url (string)
        """
        mime_type, _ = mimetypes.guess_type(file_obj.name)
        if not mime_type:
            mime_type = file_obj.content_type or 'application/octet-stream'

        # Зураг эсвэл видео гэдгийг тодорхойлох
        if mime_type.startswith('video/'):
            resource_type = 'video'
        else:
            resource_type = 'image'

        # Файлын нэрнээс extension-г хасаж public_id болгох
        name_without_ext = file_obj.name.rsplit('.', 1)[0] if '.' in file_obj.name else file_obj.name
        folder = f"bichil/hero_slider/{device}"

        result = cloudinary.uploader.upload(
            file_obj,
            resource_type=resource_type,
            folder=folder,
            public_id=name_without_ext,
            overwrite=True,
            quality='auto',
            fetch_format='auto',
        )
        return result['secure_url']

    # ─── Cloudinary helper: delete ────────────────────────────────
    def _delete_from_cloudinary(self, url):
        """
        Cloudinary URL-с public_id гаргаж аваад устгана.
        URL жишээ: https://res.cloudinary.com/bichil/image/upload/v1234/bichil/hero_slider/desktop/banner.jpg
        """
        if not url or 'cloudinary.com' not in url:
            return  # Cloudinary биш URL байвал алгасах (хуучин local файл)

        try:
            # resource_type тодорхойлох
            if '/video/upload/' in url:
                resource_type = 'video'
            else:
                resource_type = 'image'

            # URL-с public_id гаргах: /upload/vXXXX/ хэсгийн ард байгаа path
            match = re.search(r'/upload/v\d+/(.+)$', url)
            if not match:
                return

            public_id_with_ext = match.group(1)
            # Extension-г хасах
            public_id = public_id_with_ext.rsplit('.', 1)[0]

            cloudinary.uploader.destroy(public_id, resource_type=resource_type)
        except Exception as e:
            # Устгаж чадаагүй ч үндсэн ажиллагаанд нөлөөлөхгүй
            print(f"[HeroSlider] Cloudinary delete алдаа: {e}")

    # ─── CREATE ───────────────────────────────────────────────────
    def create(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        tablet_file = request.FILES.get('tablet_file')
        mobile_file = request.FILES.get('mobile_file')
        data = request.data.copy()

        if file:
            data['file'] = self._upload_to_cloudinary(file, 'desktop')
        if tablet_file:
            data['tablet_file'] = self._upload_to_cloudinary(tablet_file, 'tablet')
        if mobile_file:
            data['mobile_file'] = self._upload_to_cloudinary(mobile_file, 'mobile')

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # ─── UPDATE ───────────────────────────────────────────────────
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        file = request.FILES.get('file')
        tablet_file = request.FILES.get('tablet_file')
        mobile_file = request.FILES.get('mobile_file')

        data = request.data.copy()

        # Desktop файл — шинэ upload байвал хуучныг устгаад шинийг хадгалах
        if file:
            self._delete_from_cloudinary(instance.file)
            data['file'] = self._upload_to_cloudinary(file, 'desktop')
        else:
            data['file'] = instance.file

        # Tablet файл
        if tablet_file:
            self._delete_from_cloudinary(instance.tablet_file)
            data['tablet_file'] = self._upload_to_cloudinary(tablet_file, 'tablet')
        else:
            data['tablet_file'] = instance.tablet_file or ''

        # Mobile файл
        if mobile_file:
            self._delete_from_cloudinary(instance.mobile_file)
            data['mobile_file'] = self._upload_to_cloudinary(mobile_file, 'mobile')
        else:
            data['mobile_file'] = instance.mobile_file or ''

        # Handle type fields
        if 'tablet_type' not in data:
            data['tablet_type'] = instance.tablet_type or 'i'
        if 'mobile_type' not in data:
            data['mobile_type'] = instance.mobile_type or 'i'

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    # ─── DELETE ───────────────────────────────────────────────────
    def destroy(self, request, *args, **kwargs):
        """Slider устгахад Cloudinary дээрх файлуудыг мөн устгана."""
        instance = self.get_object()

        # Бүх device-н файлуудыг Cloudinary-с устгах
        self._delete_from_cloudinary(instance.file)
        self._delete_from_cloudinary(instance.tablet_file)
        self._delete_from_cloudinary(instance.mobile_file)

        # DB-с устгах
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
