from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as drf_filters, generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsAdminOrAgent, ReadOnlyOrAdminWrite
from accounts.views import log_activity
from .filters import PropertyFilter
from .models import (
    Amenity,
    FloorPlan,
    Property,
    PropertyComparison,
    PropertyDocument,
    PropertyImage,
    PropertyVideo,
    RecentlyViewed,
    RecentSearch,
    SavedSearch,
)
from .pagination import PropertyPagination
from .serializers import (
    AmenitySerializer,
    FloorPlanSerializer,
    PropertyComparisonSerializer,
    PropertyDetailSerializer,
    PropertyDocumentSerializer,
    PropertyImageSerializer,
    PropertyListSerializer,
    PropertyVideoSerializer,
    PropertyWriteSerializer,
    RecentlyViewedSerializer,
    RecentSearchSerializer,
    SavedSearchSerializer,
)


class AmenityViewSet(viewsets.ModelViewSet):
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    permission_classes = [ReadOnlyOrAdminWrite]


class PropertyViewSet(viewsets.ModelViewSet):
    """
    Full property CRUD + premium-platform extras:
    featured/sold toggles, bulk delete, nested media upload, similar properties.
    """

    queryset = Property.objects.all().prefetch_related("images", "amenities").select_related("agent")
    permission_classes = [ReadOnlyOrAdminWrite]
    pagination_class = PropertyPagination
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = PropertyFilter
    search_fields = ["title", "description", "address", "city"]
    ordering_fields = ["price", "created_at", "area_size", "bedrooms"]
    lookup_field = "slug"

    def get_serializer_class(self):
        if self.action == "list":
            return PropertyListSerializer
        if self.action in ("create", "update", "partial_update"):
            return PropertyWriteSerializer
        return PropertyDetailSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if not (self.request.user.is_authenticated and self.request.user.role in ("admin", "super_admin", "agent")):
            qs = qs.filter(is_active=True)
        return qs

    def list(self, request, *args, **kwargs):
        # keyword search side-effect: log recent search for authenticated users
        keyword = request.query_params.get("search")
        if keyword and request.user.is_authenticated:
            RecentSearch.objects.create(user=request.user, keyword=keyword)
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        Property.objects.filter(pk=instance.pk).update(views_count=instance.views_count + 1)
        if request.user.is_authenticated:
            RecentlyViewed.objects.update_or_create(user=request.user, property=instance)
        try:
            from analytics_app.models import PropertyView

            PropertyView.objects.create(
                property=instance,
                user=request.user if request.user.is_authenticated else None,
                ip_address=request.META.get("REMOTE_ADDR"),
            )
        except Exception:
            pass
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_create(self, serializer):
        instance = serializer.save()
        log_activity(self.request.user, "create_property", {"id": instance.id}, self.request)

    def perform_update(self, serializer):
        instance = serializer.save()
        log_activity(self.request.user, "update_property", {"id": instance.id}, self.request)

    def perform_destroy(self, instance):
        log_activity(self.request.user, "delete_property", {"id": instance.id}, self.request)
        instance.delete()

    @action(detail=True, methods=["post"], permission_classes=[IsAdminOrAgent])
    def toggle_featured(self, request, slug=None):
        prop = self.get_object()
        prop.is_featured = not prop.is_featured
        prop.save(update_fields=["is_featured"])
        return Response({"id": prop.id, "is_featured": prop.is_featured})

    @action(detail=True, methods=["post"], permission_classes=[IsAdminOrAgent])
    def toggle_sold(self, request, slug=None):
        prop = self.get_object()
        prop.is_sold = not prop.is_sold
        prop.save(update_fields=["is_sold"])
        return Response({"id": prop.id, "is_sold": prop.is_sold})

    @action(detail=False, methods=["post"], permission_classes=[IsAdminOrAgent], url_path="bulk-delete")
    def bulk_delete(self, request):
        ids = request.data.get("ids", [])
        deleted, _ = Property.objects.filter(id__in=ids).delete()
        log_activity(request.user, "bulk_delete_properties", {"ids": ids}, request)
        return Response({"deleted": deleted})

    @action(detail=True, methods=["get"], permission_classes=[AllowAny])
    def similar(self, request, slug=None):
        prop = self.get_object()
        qs = (
            Property.objects.filter(property_type=prop.property_type, is_active=True)
            .exclude(pk=prop.pk)
            .select_related("agent")
            .prefetch_related("images")[:6]
        )
        serializer = PropertyListSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["post", "delete"], parser_classes=[MultiPartParser, FormParser, JSONParser],
            permission_classes=[IsAdminOrAgent], url_path="images")
    def manage_images(self, request, slug=None):
        prop = self.get_object()
        if request.method == "DELETE":
            image_id = request.data.get("image_id")
            PropertyImage.objects.filter(pk=image_id, property=prop).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        files = request.FILES.getlist("images")
        created = []
        for f in files:
            img = PropertyImage.objects.create(property=prop, image=f)
            created.append(PropertyImageSerializer(img, context={"request": request}).data)
        return Response(created, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post", "delete"], parser_classes=[MultiPartParser, FormParser, JSONParser],
            permission_classes=[IsAdminOrAgent], url_path="videos")
    def manage_videos(self, request, slug=None):
        prop = self.get_object()
        if request.method == "DELETE":
            PropertyVideo.objects.filter(pk=request.data.get("video_id"), property=prop).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = PropertyVideoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(property=prop)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post", "delete"], parser_classes=[MultiPartParser, FormParser, JSONParser],
            permission_classes=[IsAdminOrAgent], url_path="floor-plans")
    def manage_floor_plans(self, request, slug=None):
        prop = self.get_object()
        if request.method == "DELETE":
            FloorPlan.objects.filter(pk=request.data.get("floor_plan_id"), property=prop).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = FloorPlanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(property=prop)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post", "delete"], parser_classes=[MultiPartParser, FormParser, JSONParser],
            permission_classes=[IsAdminOrAgent], url_path="documents")
    def manage_documents(self, request, slug=None):
        prop = self.get_object()
        if request.method == "DELETE":
            PropertyDocument.objects.filter(pk=request.data.get("document_id"), property=prop).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = PropertyDocumentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(property=prop)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SavedSearchViewSet(viewsets.ModelViewSet):
    serializer_class = SavedSearchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SavedSearch.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RecentSearchListView(generics.ListAPIView):
    serializer_class = RecentSearchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RecentSearch.objects.filter(user=self.request.user)[:10]


class RecentlyViewedListView(generics.ListAPIView):
    serializer_class = RecentlyViewedSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RecentlyViewed.objects.filter(user=self.request.user).select_related("property")[:20]


class PropertyComparisonView(generics.RetrieveUpdateAPIView):
    """Single 'current comparison' per user, capped at 4 properties."""

    serializer_class = PropertyComparisonSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj, _ = PropertyComparison.objects.get_or_create(user=self.request.user)
        return obj

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(self.get_serializer(instance).data)
