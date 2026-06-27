from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsAdminOrSuperAdmin, ReadOnlyOrAdminWrite
from .models import PropertyReview, Testimonial
from .serializers import PropertyReviewSerializer, TestimonialSerializer


class PropertyReviewViewSet(viewsets.ModelViewSet):
    serializer_class = PropertyReviewSerializer
    permission_classes = [ReadOnlyOrAdminWrite]

    def get_queryset(self):
        qs = PropertyReview.objects.all()
        property_id = self.request.query_params.get("property")
        if property_id:
            qs = qs.filter(property_id=property_id)
        if not (self.request.user.is_authenticated and self.request.user.role in ("admin", "super_admin")):
            qs = qs.filter(is_approved=True)
        return qs

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TestimonialViewSet(viewsets.ModelViewSet):
    serializer_class = TestimonialSerializer

    def get_queryset(self):
        qs = Testimonial.objects.all()
        if self.action == "list" and not (
            self.request.user.is_authenticated and self.request.user.role in ("admin", "super_admin")
        ):
            qs = qs.filter(is_approved=True)
        return qs

    def get_permissions(self):
        if self.action in ("list", "retrieve", "create"):
            return [AllowAny()]
        return [IsAdminOrSuperAdmin()]

    @action(detail=True, methods=["post"], permission_classes=[IsAdminOrSuperAdmin])
    def approve(self, request, pk=None):
        testimonial = self.get_object()
        testimonial.is_approved = True
        testimonial.save(update_fields=["is_approved"])
        return Response(TestimonialSerializer(testimonial).data)
