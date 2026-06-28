from rest_framework import serializers

from config.fields import SafeFileField, SafeImageField

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


class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = ["id", "name", "icon"]


class PropertyImageSerializer(serializers.ModelSerializer):
    image = SafeImageField()

    class Meta:
        model = PropertyImage
        fields = ["id", "image", "caption", "is_cover", "order"]


class PropertyVideoSerializer(serializers.ModelSerializer):
    video_file = SafeFileField(required=False, allow_null=True)

    class Meta:
        model = PropertyVideo
        fields = ["id", "video_url", "video_file", "title"]


class FloorPlanSerializer(serializers.ModelSerializer):
    image = SafeImageField()

    class Meta:
        model = FloorPlan
        fields = ["id", "image", "title", "area_size"]


class PropertyDocumentSerializer(serializers.ModelSerializer):
    file = SafeFileField()

    class Meta:
        model = PropertyDocument
        fields = ["id", "file", "title", "uploaded_at"]


class AgentMiniSerializer(serializers.Serializer):
    """Tiny agent payload embedded in property responses, avoids import cycle issues."""

    id = serializers.IntegerField()
    name = serializers.CharField()
    designation = serializers.CharField()
    photo = SafeImageField(required=False)
    phone = serializers.CharField()
    email = serializers.EmailField()


class PropertyListSerializer(serializers.ModelSerializer):
    """Lean payload for cards/grid/list view."""

    cover_image = serializers.SerializerMethodField()
    agent_name = serializers.CharField(source="agent.name", read_only=True, default=None)
    is_wishlisted = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = [
            "id", "title", "slug", "price", "listing_status", "property_type",
            "address", "city", "bedrooms", "bathrooms", "parking", "area_size",
            "is_featured", "is_sold", "cover_image", "agent_name", "is_wishlisted",
            "created_at",
        ]

    def get_cover_image(self, obj):
        cover = obj.images.filter(is_cover=True).first() or obj.images.first()
        if cover and cover.image:
            url = cover.image.url
            # Cloudinary (and any storage backend that already returns a
            # fully-qualified URL) must NOT be re-wrapped with
            # build_absolute_uri, or Render's own domain gets prepended to
            # the Cloudinary URL, producing a broken link.
            if url.startswith("http://") or url.startswith("https://"):
                return url
            request = self.context.get("request")
            return request.build_absolute_uri(url) if request else url
        return None

    def get_is_wishlisted(self, obj):
        user = self.context.get("request").user if self.context.get("request") else None
        if not user or not user.is_authenticated:
            return False
        return obj.wishlisted_by.filter(user=user).exists()


class PropertyDetailSerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)
    videos = PropertyVideoSerializer(many=True, read_only=True)
    floor_plans = FloorPlanSerializer(many=True, read_only=True)
    documents = PropertyDocumentSerializer(many=True, read_only=True)
    amenities = AmenitySerializer(many=True, read_only=True)
    agent = serializers.SerializerMethodField()
    is_wishlisted = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = [
            "id", "title", "slug", "description", "price", "listing_status", "property_type",
            "address", "city", "latitude", "longitude", "bedrooms", "bathrooms", "parking",
            "area_size", "amenities", "is_featured", "is_sold", "is_active", "views_count",
            "images", "videos", "floor_plans", "documents", "agent", "is_wishlisted",
            "average_rating", "created_at", "updated_at",
        ]

    def get_agent(self, obj):
        if not obj.agent:
            return None
        request = self.context.get("request")
        photo_url = None
        if obj.agent.photo:
            raw_url = obj.agent.photo.url
            if raw_url.startswith("http://") or raw_url.startswith("https://"):
                photo_url = raw_url
            else:
                photo_url = request.build_absolute_uri(raw_url) if request else raw_url
        return {
            "id": obj.agent.id,
            "name": obj.agent.name,
            "designation": obj.agent.designation,
            "photo": photo_url,
            "experience_years": obj.agent.experience_years,
            "phone": obj.agent.phone,
            "email": obj.agent.email,
            "facebook_url": obj.agent.facebook_url,
            "instagram_url": obj.agent.instagram_url,
            "linkedin_url": obj.agent.linkedin_url,
            "twitter_url": obj.agent.twitter_url,
        }

    def get_is_wishlisted(self, obj):
        user = self.context.get("request").user if self.context.get("request") else None
        if not user or not user.is_authenticated:
            return False
        return obj.wishlisted_by.filter(user=user).exists()

    def get_average_rating(self, obj):
        approved = obj.reviews.filter(is_approved=True)
        if not approved.exists():
            return None
        return round(sum(r.rating for r in approved) / approved.count(), 1)


class PropertyWriteSerializer(serializers.ModelSerializer):
    """Used for create/update by admin/agent. Images/docs/videos uploaded via separate nested endpoints."""

    amenity_ids = serializers.PrimaryKeyRelatedField(
        source="amenities", queryset=Amenity.objects.all(), many=True, required=False
    )

    class Meta:
        model = Property
        fields = [
            "id", "title", "description", "price", "listing_status", "property_type",
            "address", "city", "latitude", "longitude", "bedrooms", "bathrooms", "parking",
            "area_size", "amenity_ids", "is_featured", "is_sold", "is_active", "agent",
        ]

    def create(self, validated_data):
        request = self.context.get("request")
        if request:
            validated_data["created_by"] = request.user
        return super().create(validated_data)


class SavedSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedSearch
        fields = ["id", "name", "query_params", "created_at"]
        read_only_fields = ["id", "created_at"]


class RecentSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecentSearch
        fields = ["id", "keyword", "created_at"]
        read_only_fields = ["id", "created_at"]


class RecentlyViewedSerializer(serializers.ModelSerializer):
    property = PropertyListSerializer(read_only=True)

    class Meta:
        model = RecentlyViewed
        fields = ["id", "property", "viewed_at"]


class PropertyComparisonSerializer(serializers.ModelSerializer):
    properties = PropertyDetailSerializer(many=True, read_only=True)
    property_ids = serializers.PrimaryKeyRelatedField(
        source="properties", queryset=Property.objects.all(), many=True, write_only=True
    )

    class Meta:
        model = PropertyComparison
        fields = ["id", "properties", "property_ids", "created_at"]

    def validate_property_ids(self, value):
        if len(value) > 4:
            raise serializers.ValidationError("You can compare a maximum of 4 properties.")
        return value
