from rest_framework import viewsets, status, serializers as drf_serializers
from rest_framework.response import Response
from app.models.models import NewsCategory, News, NewsPageSettings
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.decorators import api_view
from app.news.category.serializers.read import NewsCategoryReadSerializer
from app.news.category.serializers.write import NewsCategoryWriteSerializer
from app.news.news.serializers.read import NewsReadSerializer
from app.news.news.serializers.write import NewsWriteSerializer
import re
from django.conf import settings as django_settings
from app.utils.storage import delete_file

class NewsCategoryViewSet(viewsets.ModelViewSet):
    queryset = NewsCategory.objects.all().prefetch_related(
        "newscategorytranslations_set",
        "newscategorytranslations_set__language"
    )

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return NewsCategoryReadSerializer
        return NewsCategoryWriteSerializer

    def create(self, request, *args, **kwargs):
        write_serializer = NewsCategoryWriteSerializer(data=request.data)
        write_serializer.is_valid(raise_exception=True)
        instance = write_serializer.save()
        
        read_serializer = NewsCategoryReadSerializer(instance)
        headers = self.get_success_headers(read_serializer.data)
        
        return Response(
            read_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        write_serializer = NewsCategoryWriteSerializer(
            instance, 
            data=request.data, 
            partial=partial
        )
        write_serializer.is_valid(raise_exception=True)
        instance = write_serializer.save()
        
        read_serializer = NewsCategoryReadSerializer(instance)
        return Response(read_serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        read_serializer = NewsCategoryReadSerializer(instance)
        data = read_serializer.data
        
        # Delete translations first (models use DO_NOTHING, DB has FK constraints)
        instance.newscategorytranslations_set.all().delete()
        
        # Check if any news uses this category — set to null instead of blocking
        News.objects.filter(category=instance).update(category=None)
        
        instance.delete()
        
        return Response(
            {
                "message": "Амжилттай устгалаа.",
                "deleted_data": data
            },
            status=status.HTTP_200_OK
        )

class NewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.all().prefetch_related(
        "newsimages_set",
        "newssocials_set",
        "newstitletranslations_set",
        "newstitletranslations_set__language",
        "newsshortdesctranslations_set",
        "newsshortdesctranslations_set__language",
        "newscontenttranslations_set",
        "newscontenttranslations_set__language"
    )
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return NewsReadSerializer
        return NewsWriteSerializer

    def create(self, request, *args, **kwargs):
        print(f"📥 NEWS CREATE - Content-Type: {request.content_type}")
        print(f"📥 NEWS CREATE - Data keys: {list(request.data.keys())}")
        write_serializer = NewsWriteSerializer(data=request.data)
        if not write_serializer.is_valid():
            print(f"❌ NEWS VALIDATION ERRORS: {write_serializer.errors}")
            return Response(write_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        instance = write_serializer.save()
        
        read_serializer = NewsReadSerializer(instance)
        headers = self.get_success_headers(read_serializer.data)
        
        return Response(
            read_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        write_serializer = NewsWriteSerializer(
            instance, 
            data=request.data, 
            partial=partial
        )
        write_serializer.is_valid(raise_exception=True)
        instance = write_serializer.save()
        
        read_serializer = NewsReadSerializer(instance)
        return Response(read_serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        read_serializer = NewsReadSerializer(instance)
        data = read_serializer.data
        
        # Delete main image
        if instance.image:
            delete_file(instance.image)
        
        # Delete additional images
        for img in instance.newsimages_set.all():
            if img.image:
                delete_file(img.image)
        
        # Manually delete all related records (models use DO_NOTHING, DB has FK constraints)
        instance.newstitletranslations_set.all().delete()
        instance.newsshortdesctranslations_set.all().delete()
        instance.newscontenttranslations_set.all().delete()
        instance.newsimages_set.all().delete()
        instance.newssocials_set.all().delete()
        
        instance.delete()
        
        return Response(
            {
                "message": "Амжилттай.",
                "deleted_data": data
            },
            status=status.HTTP_200_OK
        )


class NewsPageSettingsSerializer(drf_serializers.ModelSerializer):
    class Meta:
        model = NewsPageSettings
        fields = ('id', 'latest_heading', 'featured_heading', 'latest_heading_en', 'featured_heading_en',
                  'section_label_color', 'section_label_size', 'heading_color', 'heading_size',
                  'divider_color', 'button_color', 'button_text_color', 'button_size')


@api_view(['GET', 'PUT'])
def news_page_settings_view(request):
    settings, _ = NewsPageSettings.objects.get_or_create(id=1, defaults={
        'latest_heading': 'Сүүлийн мэдээнүүд',
        'featured_heading': 'Онцлох мэдээ',
        'latest_heading_en': '',
        'featured_heading_en': '',
    })
    
    if request.method == 'GET':
        serializer = NewsPageSettingsSerializer(settings)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = NewsPageSettingsSerializer(settings, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)