from rest_framework import viewsets
from app.models.models import Category
from app.categories.serializers.read import CategoryReadSerializer
from app.categories.serializers.write import CategoryWriteSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().prefetch_related(
        'categorytranslations_set',
        'categorytranslations_set__language',
        'producttype_set',
        'producttype_set__producttypetranslations_set',
        'producttype_set__producttypetranslations_set__language',
        'producttype_set__product_set',
        'producttype_set__product_set__producttranslations_set',
    )

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return CategoryReadSerializer
        return CategoryWriteSerializer
