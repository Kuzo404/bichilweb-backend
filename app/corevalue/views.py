from rest_framework import viewsets
from app.models.models import CoreValue
from app.corevalue.serializers import CoreValueReadSerializer, CoreValueWriteSerializer


class CoreValueViewSet(viewsets.ModelViewSet):
    queryset = CoreValue.objects.all().prefetch_related(
        'corevaluetitletranslations_set',
        'corevaluetitletranslations_set__language',
        'corevaluedesctranslations_set',
        'corevaluedesctranslations_set__language',
    ).order_by('index', 'id')

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return CoreValueReadSerializer
        return CoreValueWriteSerializer
