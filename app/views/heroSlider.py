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

    # Видео хамгийн их хэмжээ (100MB = ~2 минут MP4)
    MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100MB

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

        is_video = mime_type.startswith('video/')
        resource_type = 'video' if is_video else 'image'

        # Видео хэмжээ шалгах
        if is_video and hasattr(file_obj, 'size') and file_obj.size > self.MAX_VIDEO_SIZE:
            raise ValueError(
                f'Видео хэт том байна ({file_obj.size / (1024*1024):.1f}MB). '
                f'Хамгийн ихдээ {self.MAX_VIDEO_SIZE / (1024*1024):.0f}MB (~2 мин) байх ёстой.'
            )

        # Файлын нэрнээс extension-г хасаж public_id болгох
        name_without_ext = file_obj.name.rsplit('.', 1)[0] if '.' in file_obj.name else file_obj.name
        folder = f"bichil/hero_slider/{device}"

        if is_video:
            # Видео: upload_large() ашиглан chunk-аар илгээх (20MB chunk)
            result = cloudinary.uploader.upload_large(
                file_obj,
                resource_type=resource_type,
                folder=folder,
                public_id=name_without_ext,
                overwrite=True,
                chunk_size=20_000_000,  # 20MB chunk
                timeout=300,  # 5 минут timeout
            )
        else:
            # Зураг: ердийн upload
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

        try:
            if file:
                data['file'] = self._upload_to_cloudinary(file, 'desktop')
            if tablet_file:
                data['tablet_file'] = self._upload_to_cloudinary(tablet_file, 'tablet')
            if mobile_file:
                data['mobile_file'] = self._upload_to_cloudinary(mobile_file, 'mobile')
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'detail': f'Cloudinary upload алдаа: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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

        try:
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
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'detail': f'Cloudinary upload алдаа: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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
