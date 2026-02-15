"""
Management Member CRUD view.
Зургийг Cloudinary дээр хадгалаад, устгахад Cloudinary-с устгана.
"""
import re
from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
import cloudinary
import cloudinary.uploader
from django.conf import settings

from app.models.models import ManagementMember, ManagementMemberTranslations
from app.management.serializers import ManagementMemberReadSerializer
from app.management.write_serializers import ManagementMemberWriteSerializer

# Cloudinary config
cloudinary.config(
    cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
    api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
    api_secret=settings.CLOUDINARY_STORAGE['API_SECRET'],
)


class ManagementMemberViewSet(viewsets.ModelViewSet):
    queryset = ManagementMember.objects.all().prefetch_related(
        'managementmembertranslations_set',
        'managementmembertranslations_set__language',
    ).order_by('sort_order', 'id')
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ManagementMemberReadSerializer
        return ManagementMemberWriteSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        member_type = self.request.query_params.get('type')
        if member_type:
            qs = qs.filter(type=member_type)
        return qs

    # ─── Cloudinary helper: upload ────────────────────────────────
    def _upload_to_cloudinary(self, file_obj):
        name_without_ext = file_obj.name.rsplit('.', 1)[0] if '.' in file_obj.name else file_obj.name
        folder = "bichil/management"

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
            print(f"[Management] Cloudinary delete алдаа: {e}")

    # ─── CREATE ───────────────────────────────────────────────────
    def create(self, request, *args, **kwargs):
        data = self._build_data(request)
        image_file = request.FILES.get('image_file')

        try:
            if image_file:
                cloudinary_url = self._upload_to_cloudinary(image_file)
                data['image'] = cloudinary_url
        except Exception as e:
            return Response(
                {'detail': f'Cloudinary upload алдаа: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        serializer = self.get_serializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        read_serializer = ManagementMemberReadSerializer(serializer.instance)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    # ─── UPDATE ───────────────────────────────────────────────────
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = self._build_data(request)
        image_file = request.FILES.get('image_file')

        try:
            if image_file:
                self._delete_from_cloudinary(instance.image)
                cloudinary_url = self._upload_to_cloudinary(image_file)
                data['image'] = cloudinary_url
        except Exception as e:
            return Response(
                {'detail': f'Cloudinary upload алдаа: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        serializer = self.get_serializer(
            instance, data=data, partial=partial, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        read_serializer = ManagementMemberReadSerializer(serializer.instance)
        return Response(read_serializer.data)

    # ─── DELETE ───────────────────────────────────────────────────
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self._delete_from_cloudinary(instance.image)
        ManagementMemberTranslations.objects.filter(member=instance).delete()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ─── Build plain dict from request data ─────────────────────────
    def _build_data(self, request):
        """
        QueryDict (FormData) → plain dict.
        FormData-аар translations[0][language]=1, translations[0][name]=... гэж
        ирэхээр nested list рүү хөрвүүлнэ.
        JSON body байвал шууд буцаана.
        """
        import json

        raw = request.data

        # JSON body — already a plain dict with proper nesting
        if request.content_type and 'application/json' in request.content_type:
            if isinstance(raw, dict):
                return dict(raw)
            return raw

        # Convert QueryDict to plain dict (single values)
        data = {}
        translations = {}

        for key in raw.keys():
            m = re.match(r'translations\[(\d+)\]\[(\w+)\]', key)
            if m:
                idx = int(m.group(1))
                field = m.group(2)
                if idx not in translations:
                    translations[idx] = {}
                val = raw[key]
                # Convert language to int for PrimaryKeyRelatedField
                if field == 'language':
                    try:
                        val = int(val)
                    except (ValueError, TypeError):
                        pass
                translations[idx][field] = val
            else:
                val = raw[key]
                # Convert known fields
                if key == 'sort_order':
                    try:
                        val = int(val)
                    except (ValueError, TypeError):
                        val = 0
                elif key == 'active':
                    val = str(val).lower() in ('true', '1', 'yes')
                data[key] = val

        if translations:
            data['translations'] = [translations[i] for i in sorted(translations.keys())]
        elif 'translations' in data:
            # Could be JSON string
            val = data['translations']
            if isinstance(val, str):
                try:
                    data['translations'] = json.loads(val)
                except (json.JSONDecodeError, ValueError):
                    data['translations'] = []

        return data
