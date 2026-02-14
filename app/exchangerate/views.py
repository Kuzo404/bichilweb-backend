from rest_framework import viewsets
from app.models.models import ExchangeRateConfig
from app.exchangerate.serializers import ExchangeRateConfigSerializer, ExchangeRateConfigWriteSerializer


class ExchangeRateConfigViewSet(viewsets.ModelViewSet):
    queryset = ExchangeRateConfig.objects.all().order_by('id')

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ExchangeRateConfigSerializer
        return ExchangeRateConfigWriteSerializer
