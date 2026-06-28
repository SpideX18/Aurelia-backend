from rest_framework import serializers

from config.fields import SafeImageField

from .models import SiteSettings


class SiteSettingsSerializer(serializers.ModelSerializer):
    logo = SafeImageField(required=False, allow_null=True)

    class Meta:
        model = SiteSettings
        fields = [
            "company_name", "logo", "tagline", "contact_email", "contact_phone", "address",
            "facebook_url", "instagram_url", "linkedin_url", "twitter_url", "youtube_url",
            "seo_title", "seo_description", "seo_keywords", "updated_at",
        ]
