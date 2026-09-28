from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.core.mixins import PartialUpdateMixin
from apps.core.permissions import IsCreatorOrReadOnly
from .models import Doctor
from .serializers import DoctorSerializer


@extend_schema_view(update=extend_schema(request=DoctorSerializer(partial=True)))
class DoctorViewSet(PartialUpdateMixin, viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated, IsCreatorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
