from rest_framework import serializers

from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    property_title = serializers.CharField(source="property.title", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)
    agent_name = serializers.CharField(source="agent.name", read_only=True, default=None)

    class Meta:
        model = Appointment
        fields = [
            "id", "user", "user_email", "property", "property_title", "agent", "agent_name",
            "visit_date", "visit_time", "notes", "status", "admin_note", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "status", "admin_note", "created_at", "updated_at"]


class AppointmentStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Appointment.Status.choices)
    admin_note = serializers.CharField(required=False, allow_blank=True)
