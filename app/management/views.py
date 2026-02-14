from rest_framework import viewsets
from app.models.models import ManagementMember
from app.management.serializers import ManagementMemberReadSerializer
from app.management.write_serializers import ManagementMemberWriteSerializer


class ManagementMemberViewSet(viewsets.ModelViewSet):
    queryset = ManagementMember.objects.all().prefetch_related(
        'managementmembertranslations_set',
        'managementmembertranslations_set__language',
    ).order_by('sort_order', 'id')

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ManagementMemberReadSerializer
        return ManagementMemberWriteSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        member_type = self.request.query_params.get('type')
        if member_type:
            qs = qs.filter(type=member_type)
        return qs
