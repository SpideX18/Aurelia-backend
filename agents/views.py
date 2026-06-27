from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsAdminOrSuperAdmin, ReadOnlyOrAdminWrite
from properties.models import Property
from properties.serializers import PropertyListSerializer
from .models import Agent, AgentReview
from .serializers import AgentDetailSerializer, AgentListSerializer, AgentReviewSerializer


class AgentViewSet(viewsets.ModelViewSet):
    queryset = Agent.objects.all()
    permission_classes = [ReadOnlyOrAdminWrite]

    def get_serializer_class(self):
        if self.action == "list":
            return AgentListSerializer
        return AgentDetailSerializer

    @action(detail=True, methods=["get"])
    def listings(self, request, pk=None):
        agent = self.get_object()
        qs = Property.objects.filter(agent=agent, is_active=True)
        serializer = PropertyListSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminOrSuperAdmin], url_path="assign-property")
    def assign_property(self, request, pk=None):
        agent = self.get_object()
        property_id = request.data.get("property_id")
        prop = Property.objects.filter(pk=property_id).first()
        if not prop:
            return Response({"detail": "Property not found."}, status=404)
        prop.agent = agent
        prop.save(update_fields=["agent"])
        return Response({"detail": f"Assigned {prop.title} to {agent.name}."})


class AgentReviewViewSet(viewsets.ModelViewSet):
    queryset = AgentReview.objects.all()
    serializer_class = AgentReviewSerializer
    permission_classes = [ReadOnlyOrAdminWrite]

    def get_queryset(self):
        qs = super().get_queryset()
        agent_id = self.request.query_params.get("agent")
        if agent_id:
            qs = qs.filter(agent_id=agent_id)
        if not (self.request.user.is_authenticated and self.request.user.role in ("admin", "super_admin")):
            qs = qs.filter(is_approved=True)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated()]
        return super().get_permissions()
