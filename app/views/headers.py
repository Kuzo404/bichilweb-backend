from rest_framework import viewsets, status
from rest_framework.response import Response
from app.models.models import Header
from app.serializers.headers import HeaderSerializer, HeaderCreateUpdateSerializer
import traceback

# ============================================================================
# HEADER VIEWSET
# ============================================================================
# GET  /api/v1/headers/       → Бүх header өгөгдлийг буцаана (menus + styles)
# POST /api/v1/headers/       → Шинэ header үүсгэх
# PUT  /api/v1/headers/{id}/  → Header шинэчлэх
# DELETE /api/v1/headers/{id}/ → Header устгах
# ============================================================================

# Өгөгдлийн сан холболт алдаа гарвал буцаах хоосон бүтэц
EMPTY_HEADER = {
    'id': None,
    'logo': '',
    'active': 1,
    'menus': [],
    'styles': []
}


class HeaderViewSet(viewsets.ModelViewSet):
    queryset = Header.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return HeaderCreateUpdateSerializer
        return HeaderSerializer

    def list(self, request, *args, **kwargs):
        """
        Өгөгдлийн сангаас header мэдээллийг буцаана.
        - Ганц Header (id=1) байдаг гэж үзнэ
        - menus болон styles-ийг nested JSON байдлаар буцаана
        - Алдаа гарвал хоосон бүтэц буцаана (500 биш!)
        """
        try:
            # Өгөгдлийн сангаас header авах
            header = Header.objects.filter(id=1).first()
            if not header:
                header = Header.objects.first()

            if not header:
                return Response([EMPTY_HEADER])

            serializer = self.get_serializer(header)
            # ⚠️ serializer.data-г ЭНД evaluate хийх ёстой (try блок дотор)
            # Хэрвээ DB баганы алдаа (max_width, logo_size г.м.) байвал энд барина
            result_data = serializer.data
            return Response([result_data])

        except Exception as e:
            print(f'❌ Header list алдаа: {e}')
            traceback.print_exc()
            # Алдаа гарсан ч хоосон бүтэц буцааж 500 гаргахгүй
            return Response([EMPTY_HEADER])

    def retrieve(self, request, *args, **kwargs):
        """
        Нэг header-ийн мэдээллийг буцаана.
        GET /api/v1/headers/{id}/
        """
        try:
            header = self.get_object()
            serializer = self.get_serializer(header)
            result_data = serializer.data
            return Response(result_data)
        except Exception as e:
            print(f'❌ Header retrieve алдаа: {e}')
            traceback.print_exc()
            return Response(EMPTY_HEADER)

    def destroy(self, request, *args, **kwargs):
        header = self.get_object()
        header.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
