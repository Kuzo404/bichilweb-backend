from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from app.models.models import AppDownload
from app.serializers.appDownload import AppDownloadReadSerializer, AppDownloadWriteSerializer


class AppDownloadViewSet(viewsets.ModelViewSet):
    queryset = AppDownload.objects.prefetch_related('titles', 'lists').all()
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return AppDownloadReadSerializer
        return AppDownloadWriteSerializer
