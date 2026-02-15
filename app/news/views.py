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
import cloudinary
import cloudinary.uploader
from django.conf import settings as django_settings

# Cloudinary config
cloudinary.config(
    cloud_name=django_settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
    api_key=django_settings.CLOUDINARY_STORAGE['API_KEY'],
    api_secret=django_settings.CLOUDINARY_STORAGE['API_SECRET'],
)

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
        
        # Delete image from Cloudinary if it's a Cloudinary URL
        if instance.image:
            if 'cloudinary.com' in str(instance.image):
                try:
                    match = re.search(r'/upload/v\d+/(.+)$', instance.image)
                    if match:
                        public_id_with_ext = match.group(1)
                        public_id = public_id_with_ext.rsplit('.', 1)[0]
                        cloudinary.uploader.destroy(public_id, resource_type='image')
                        print(f"\u2705 News Cloudinary image deleted: {public_id}")
                except Exception as e:
                    print(f"\u274c News Cloudinary delete error: {e}")
        
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
        fields = ('id', 'latest_heading', 'featured_heading')


@api_view(['GET', 'PUT'])
def news_page_settings_view(request):
    settings, _ = NewsPageSettings.objects.get_or_create(id=1, defaults={
        'latest_heading': 'Сүүлийн мэдээнүүд',
        'featured_heading': 'Онцлох мэдээ',
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