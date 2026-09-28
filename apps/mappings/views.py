from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, extend_schema, inline_serializer
from rest_framework import generics, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.doctors.serializers import DoctorSerializer
from apps.patients.models import Patient
from .models import PatientDoctorMapping
from .serializers import MappingSerializer


class MappingListCreateView(generics.ListCreateAPIView):
    serializer_class = MappingSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return PatientDoctorMapping.objects.none()
        return PatientDoctorMapping.objects.filter(
            patient__created_by=self.request.user
        ).select_related("patient", "doctor")

    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)


class MappingDetailView(APIView):
    """GET takes a patient id, DELETE takes a mapping id."""

    @extend_schema(
        summary="List doctors assigned to a patient",
        parameters=[OpenApiParameter("id", int, OpenApiParameter.PATH, description="Patient ID")],
        responses=inline_serializer(
            "PatientDoctorsResponse",
            {
                "patient_id": serializers.IntegerField(),
                "patient_name": serializers.CharField(),
                "doctors": DoctorSerializer(many=True),
            },
        ),
    )
    def get(self, request, pk):
        patient = get_object_or_404(Patient, pk=pk, created_by=request.user)
        mappings = patient.doctor_mappings.select_related("doctor")
        return Response({
            "patient_id": patient.id,
            "patient_name": patient.name,
            "doctors": [
                {"mapping_id": m.id, **DoctorSerializer(m.doctor).data} for m in mappings
            ],
        })

    @extend_schema(
        summary="Remove a doctor from a patient",
        parameters=[OpenApiParameter("id", int, OpenApiParameter.PATH, description="Mapping ID")],
        responses=inline_serializer("MessageResponse", {"message": serializers.CharField()}),
    )
    def delete(self, request, pk):
        mapping = get_object_or_404(PatientDoctorMapping, pk=pk, patient__created_by=request.user)
        mapping.delete()
        return Response({"message": "Doctor removed from patient"}, status=status.HTTP_200_OK)
