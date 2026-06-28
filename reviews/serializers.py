from rest_framework import serializers

from config.fields import SafeImageField

from .models import PropertyReview, Testimonial


class PropertyReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = PropertyReview
        fields = ["id", "property", "user", "user_name", "rating", "comment", "is_approved", "created_at"]
        read_only_fields = ["id", "is_approved", "created_at"]


class TestimonialSerializer(serializers.ModelSerializer):
    photo = SafeImageField(required=False, allow_null=True)

    class Meta:
        model = Testimonial
        fields = ["id", "name", "location", "photo", "rating", "text", "is_approved", "created_at"]
        read_only_fields = ["id", "created_at"]
