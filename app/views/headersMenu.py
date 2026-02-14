from rest_framework import viewsets
from django.db.models import Q
from app.models.models import HeaderMenu
from app.serializers.headersMenu import HeaderMenuSerializer

class HeaderMenuViewSet(viewsets.ModelViewSet):
    queryset = HeaderMenu.objects.all()
    serializer_class = HeaderMenuSerializer
    
    def get_queryset(self):
        """
        Filter HeaderMenu objects by header_id if provided in query params.
        Usage: GET /api/v1/header-menu/?header_id=1
        """
        queryset = HeaderMenu.objects.all()
        header_id = self.request.query_params.get('header_id')
        
        if header_id:
            try:
                queryset = queryset.filter(header_id=int(header_id))
            except (ValueError, TypeError):
                pass
        
        return queryset
