from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
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

    @action(detail=False, methods=['delete'])
    def bulk_delete(self, request):
        """Delete all menus for a given header_id. CASCADE handles submenus & tertiary."""
        header_id = request.query_params.get('header_id')
        if not header_id:
            return Response({'error': 'header_id required'}, status=status.HTTP_400_BAD_REQUEST)
        deleted_count, _ = HeaderMenu.objects.filter(header_id=int(header_id)).delete()
        return Response({'deleted': deleted_count}, status=status.HTTP_200_OK)
