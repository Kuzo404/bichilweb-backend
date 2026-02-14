from rest_framework import viewsets
from app.models.models import LoanCalculatorConfig
from app.calculator.serializers import LoanCalculatorConfigSerializer, LoanCalculatorConfigWriteSerializer


class LoanCalculatorConfigViewSet(viewsets.ModelViewSet):
    queryset = LoanCalculatorConfig.objects.all().order_by('id')

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return LoanCalculatorConfigSerializer
        return LoanCalculatorConfigWriteSerializer
