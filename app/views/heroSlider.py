from rest_framework.viewsets import ModelViewSet
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
import os

from app.models.models import HeroSlider
from app.serializers.heroSlider import HeroSliderSerializer


class HeroSliderViewSet(ModelViewSet):
    queryset = HeroSlider.objects.all()
    serializer_class = HeroSliderSerializer
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        tablet_file = request.FILES.get('tablet_file')
        mobile_file = request.FILES.get('mobile_file')
        data = request.data.copy()  
        if file:
            save_path = self._save_file(file)
            data['file'] = save_path
        if tablet_file:
            data['tablet_file'] = self._save_file(tablet_file)
        if mobile_file:
            data['mobile_file'] = self._save_file(mobile_file)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        file = request.FILES.get('file')
        tablet_file = request.FILES.get('tablet_file')
        mobile_file = request.FILES.get('mobile_file')

        data = request.data.copy()
        if file:
            data['file'] = self._save_file(file)
        else:
            data['file'] = instance.file

        if tablet_file:
            data['tablet_file'] = self._save_file(tablet_file)
        else:
            data['tablet_file'] = instance.tablet_file or ''

        if mobile_file:
            data['mobile_file'] = self._save_file(mobile_file)
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

    def _save_file(self, file):
        """Файлыг хадгалах helper function"""
        save_folder = 'media/hero_sliders'
        os.makedirs(save_folder, exist_ok=True)
        save_path = os.path.join(save_folder, file.name)
        with open(save_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        # return relative path for Image URL
        return save_path.replace('\\', '/')  # Windows-д path засах
