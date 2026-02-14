from rest_framework import viewsets
from rest_framework.response import Response
from app.models.models import OrgStructure
from app.orgstructure.serializers import OrgStructureSerializer


class OrgStructureViewSet(viewsets.ModelViewSet):
    queryset = OrgStructure.objects.all()
    serializer_class = OrgStructureSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        page = self.request.query_params.get('page')
        if page:
            qs = qs.filter(page_id=page)
        return qs
