from rest_framework import viewsets, status
from rest_framework.response import Response
from app.models.models import Header
from app.serializers.headers import HeaderSerializer, HeaderCreateUpdateSerializer

class HeaderViewSet(viewsets.ModelViewSet):
    queryset = Header.objects.all()
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return HeaderCreateUpdateSerializer
        return HeaderSerializer

    def list(self, request, *args, **kwargs):
        """
        LIST дээ header data-г buцаадаг. 
        Энэ нь admin эсвэл frontend-ээс өгөгдлийг авахад ашигладаг.
        Ганц Header (id=1) байдаг гэж үзнэ, эхний header буцаана.
        """
        try:
            # ID=1 header авах (системийн үндсэн header)
            header = Header.objects.filter(id=1).first()
            if not header:
                # Байхгүй бол эхний header авна
                header = Header.objects.first()
            
            if header:
                serializer = self.get_serializer(header)
                return Response([serializer.data])
            else:
                # Дуктхүүлэхгүй бүтэц буцаана
                return Response([{
                    'id': None,
                    'logo': '',
                    'active': 1,
                    'menus': [],
                    'styles': []
                }])
        except Exception as e:
            print(f'Error in list: {e}')
            return Response([{
                'id': None,
                'logo': '',
                'active': 1,
                'menus': [],
                'styles': []
            }])

    def destroy(self, request, *args, **kwargs):
        header = self.get_object()
        header.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
