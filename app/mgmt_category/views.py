from rest_framework import viewsets
from app.models.models import ManagementCategory
from app.mgmt_category.serializers import ManagementCategoryReadSerializer, ManagementCategoryWriteSerializer


class ManagementCategoryViewSet(viewsets.ModelViewSet):
    queryset = ManagementCategory.objects.all().prefetch_related(
        'managementcategorytranslations_set',
        'managementcategorytranslations_set__language',
    ).order_by('sort_order', 'id')

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ManagementCategoryReadSerializer
        return ManagementCategoryWriteSerializer
