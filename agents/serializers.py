from rest_framework import serializers

from config.fields import SafeImageField

from .models import Agent, AgentReview


class AgentReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = AgentReview
        fields = ["id", "agent", "user", "user_name", "rating", "comment", "is_approved", "created_at"]
        read_only_fields = ["id", "is_approved", "created_at"]


class AgentListSerializer(serializers.ModelSerializer):
    active_listings_count = serializers.ReadOnlyField()
    sold_count = serializers.ReadOnlyField()
    photo = SafeImageField(required=False, allow_null=True)

    class Meta:
        model = Agent
        fields = [
            "id", "name", "designation", "photo", "experience_years",
            "phone", "email", "is_active", "active_listings_count", "sold_count",
        ]


class AgentDetailSerializer(serializers.ModelSerializer):
    active_listings_count = serializers.ReadOnlyField()
    sold_count = serializers.ReadOnlyField()
    reviews = AgentReviewSerializer(many=True, read_only=True)
    photo = SafeImageField(required=False, allow_null=True)

    class Meta:
        model = Agent
        fields = [
            "id", "user", "name", "designation", "photo", "experience_years", "biography",
            "phone", "email", "facebook_url", "instagram_url", "linkedin_url", "twitter_url",
            "is_active", "active_listings_count", "sold_count", "reviews", "created_at",
        ]
