from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsAdminOrAgent
from accounts.views import log_activity
from .models import Appointment
from .serializers import AppointmentSerializer, AppointmentStatusSerializer


class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Appointment.objects.select_related("property", "agent", "user")
        if user.role in ("admin", "super_admin"):
            return qs
        if user.role == "agent":
            return qs.filter(agent__user=user)
        return qs.filter(user=user)

    def perform_create(self, serializer):
        instance = serializer.save(user=self.request.user, property_id=self.request.data.get("property"))
        log_activity(self.request.user, "schedule_visit", {"appointment_id": instance.id}, self.request)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminOrAgent], url_path="update-status")
    def update_status(self, request, pk=None):
        appointment = self.get_object()
        serializer = AppointmentStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment.status = serializer.validated_data["status"]
        appointment.admin_note = serializer.validated_data.get("admin_note", appointment.admin_note)
        appointment.save(update_fields=["status", "admin_note", "updated_at"])
        log_activity(
            request.user, "update_appointment_status",
            {"appointment_id": appointment.id, "status": appointment.status}, request,
        )
        return Response(AppointmentSerializer(appointment).data)
