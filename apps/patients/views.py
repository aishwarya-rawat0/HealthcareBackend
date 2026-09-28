from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from apps.core.mixins import PartialUpdateMixin
from .models import Patient
from .serializers import PatientSerializer


@extend_schema_view(update=extend_schema(request=PatientSerializer(partial=True)))
class PatientViewSet(PartialUpdateMixin, viewsets.ModelViewSet):
    serializer_class = PatientSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Patient.objects.none()
        return Patient.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
